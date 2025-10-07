// Global variables
let raceData = [];
let filteredData = [];
let charts = {};
let currentRaceFile = '../data/639.json'; // Default to 10K
let currentRaceName = '10K';

// Toast notification system
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';

    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Show/hide loading overlay
function showLoading() {
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

// Calculate pace (min/km)
function calculatePace(timeStr, distance) {
    const seconds = timeToSeconds(timeStr);
    if (!seconds || !distance) return null;
    const paceSeconds = seconds / distance;
    const minutes = Math.floor(paceSeconds / 60);
    const secs = Math.floor(paceSeconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

// Get race distance
function getRaceDistance() {
    const distances = {
        '10k': 10,
        '21k': 21.0975,
        '42k': 42.195
    };
    return distances[currentRaceName.toLowerCase()] || 10;
}

// URL parameter handling
function getUrlParameter(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

function setUrlParameter(name, value) {
    const url = new URL(window.location);
    url.searchParams.set(name, value);
    window.history.pushState({}, '', url);
}

function setMultipleUrlParameters(params) {
    const url = new URL(window.location);
    Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
            url.searchParams.set(key, params[key]);
        }
    });
    window.history.pushState({}, '', url);
}

function clearUrlParameters() {
    const url = new URL(window.location);
    url.search = '';
    window.history.pushState({}, '', url);
}

// Get race file from race name
function getRaceFile(raceName) {
    const raceFiles = {
        '10k': '../data/639.json',
        '21k': '../data/635.json',
        '42k': '../data/636.json'
    };
    return raceFiles[raceName.toLowerCase()] || '../data/639.json';
}

// Load and parse race data
async function loadRaceData(raceFile = currentRaceFile) {
    showLoading();

    try {
        const response = await fetch(raceFile);

        if (!response.ok) {
            showToast(`Failed to load race data. Please ensure ${raceFile} is in the same directory.`, 'error');
            console.error(`HTTP error! status: ${response.status}`);
            hideLoading();
            return;
        }

        const jsonData = await response.json();

    // Parse the data structure
    const header = jsonData.header;
    const data = jsonData.data;

    // Map data to structured objects
    raceData = data.map(row => ({
        registrationId: row[0],
        bib: parseInt(row[1]),
        lastname: row[2],
        firstname: row[3],
        gender: row[4],
        nationality: row[5],
        gunResult: row[6],
        chipResult: row[7], // Real time - prioritized for analysis
        overallRank: parseInt(row[8]),
        genderRank: parseInt(row[9]),
        category: row[10],
        categoryRank: parseInt(row[11])
    }));

        filteredData = [...raceData];
        currentRaceFile = raceFile;
        initializeApp();

        hideLoading();

        // Check for URL parameters after data is loaded
        const bibParam = getUrlParameter('bib');
        if (bibParam) {
            const bib = parseInt(bibParam);
            const participant = raceData.find(p => p.bib === bib);
            if (participant) {
                displayParticipantResults(participant);
                // Don't show toast if we're loading from URL param
            } else {
                showToast(`Participant with bib ${bib} not found`, 'error');
            }
        } else {
            // Only show success toast if not loading from URL param
            showToast(`${currentRaceName} race data loaded successfully!`, 'success');
        }
    } catch (error) {
        hideLoading();
        showToast(`Error loading race data: ${error.message}`, 'error');
        console.error('Error loading race data:', error);
    }
}

// Initialize the application
function initializeApp() {
    populateFilters();
    displayOverallStats();
    renderLeaderboard('overall');
    createCharts();
}

// Populate filter dropdowns
function populateFilters() {
    // Clear existing options (except the "All" option)
    const categoryFilter = document.getElementById('categoryFilter');
    const nationalityFilter = document.getElementById('nationalityFilter');

    // Keep only the first option ("All")
    categoryFilter.innerHTML = '<option value="all">All Categories</option>';
    nationalityFilter.innerHTML = '<option value="all">All Countries</option>';

    // Categories
    const categories = [...new Set(raceData.map(p => p.category))].sort();
    categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        categoryFilter.appendChild(option);
    });

    // Nationalities
    const nationalities = [...new Set(raceData.map(p => p.nationality))].sort();
    nationalities.forEach(nat => {
        const option = document.createElement('option');
        option.value = nat;
        option.textContent = nat;
        nationalityFilter.appendChild(option);
    });
}

// Convert time string to seconds
function timeToSeconds(timeStr) {
    if (!timeStr) return null;
    const parts = timeStr.split(':');
    if (parts.length === 3) {
        return parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2]);
    }
    return null;
}

// Convert seconds to time string
function secondsToTime(seconds) {
    if (!seconds) return 'N/A';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Calculate percentile
function calculatePercentile(rank, total) {
    return ((1 - (rank - 1) / total) * 100).toFixed(1);
}

// Search by bib number
function searchByBib() {
    const bibNumber = parseInt(document.getElementById('bibSearch').value);
    if (!bibNumber) {
        showToast('Please enter a valid bib number', 'error');
        return;
    }

    const participant = raceData.find(p => p.bib === bibNumber);
    if (participant) {
        displayParticipantResults(participant);
        updateUrlWithCurrentState(bibNumber);
    } else {
        showToast(`No participant found with bib number ${bibNumber}`, 'error');
    }
}

// Update URL with all current state
function updateUrlWithCurrentState(bib = null) {
    const params = {
        race: currentRaceName
    };

    if (bib) {
        params.bib = bib;
    }

    // Add filters if not "all"
    const genderFilter = document.getElementById('genderFilter').value;
    const categoryFilter = document.getElementById('categoryFilter').value;
    const nationalityFilter = document.getElementById('nationalityFilter').value;

    if (genderFilter !== 'all') params.gender = genderFilter;
    if (categoryFilter !== 'all') params.category = categoryFilter;
    if (nationalityFilter !== 'all') params.nationality = nationalityFilter;

    setMultipleUrlParameters(params);
}

// Search by name
function searchByName() {
    const searchName = document.getElementById('nameSearch').value.toLowerCase().trim();
    if (!searchName) {
        showToast('Please enter a name', 'error');
        return;
    }

    const matches = raceData.filter(p =>
        p.firstname.toLowerCase().includes(searchName) ||
        p.lastname.toLowerCase().includes(searchName)
    );

    if (matches.length === 1) {
        displayParticipantResults(matches[0]);
        updateUrlWithCurrentState(matches[0].bib);
    } else if (matches.length > 1) {
        displayMultipleMatches(matches);
        showToast(`Found ${matches.length} participants matching "${searchName}"`, 'info');
    } else {
        showToast(`No participant found with name "${searchName}"`, 'error');
    }
}

// Clear search results
function clearSearch() {
    document.getElementById('bibSearch').value = '';
    document.getElementById('nameSearch').value = '';
    document.getElementById('participantResults').classList.add('hidden');
    clearUrlParameters();
    showToast('Search cleared', 'info');
}

// Display multiple name matches
function displayMultipleMatches(matches) {
    const resultsSection = document.getElementById('participantResults');
    const card = document.getElementById('participantCard');

    let html = `<h3>Multiple matches found (${matches.length}):</h3><div class="matches-list">`;
    matches.forEach(p => {
        html += `
            <div class="match-item" onclick="selectParticipant(${p.bib})">
                <strong>${p.firstname} ${p.lastname}</strong> - Bib: ${p.bib} - ${p.chipResult}
            </div>
        `;
    });
    html += '</div>';

    card.innerHTML = html;
    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Select participant from multiple matches
function selectParticipant(bib) {
    const participant = raceData.find(x => x.bib === bib);
    if (participant) {
        displayParticipantResults(participant);
        updateUrlWithCurrentState(bib);
    }
}

// Print participant results
function printResults() {
    window.print();
}

// Share participant results
function shareResults(bib) {
    // Use current URL which already has all parameters
    const currentUrl = window.location.href;
    navigator.clipboard.writeText(currentUrl).then(() => {
        showToast('Link copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy link', 'error');
    });
}

// Display participant results
function displayParticipantResults(participant) {
    const resultsSection = document.getElementById('participantResults');
    const card = document.getElementById('participantCard');

    const overallPercentile = calculatePercentile(participant.overallRank, raceData.length);
    const genderCount = raceData.filter(p => p.gender === participant.gender).length;
    const genderPercentile = calculatePercentile(participant.genderRank, genderCount);
    const categoryCount = raceData.filter(p => p.category === participant.category).length;
    const categoryPercentile = calculatePercentile(participant.categoryRank, categoryCount);

    const timeDiff = timeToSeconds(participant.gunResult) - timeToSeconds(participant.chipResult);
    const distance = getRaceDistance();
    const pace = calculatePace(participant.chipResult, distance);

    card.innerHTML = `
        <div class="participant-header">
            <h3>${participant.firstname} ${participant.lastname}</h3>
            <span class="bib-badge">Bib #${participant.bib}</span>
        </div>

        <div class="participant-details">
            <div class="detail-row">
                <span class="label">Gender:</span>
                <span class="value">${participant.gender === 'M' ? 'Male' : 'Female'}</span>
            </div>
            <div class="detail-row">
                <span class="label">Category:</span>
                <span class="value">${participant.category}</span>
            </div>
            <div class="detail-row">
                <span class="label">Nationality:</span>
                <span class="value">${participant.nationality}</span>
            </div>
        </div>

        <div class="time-stats">
            <div class="time-card">
                <div class="time-label">Chip Time (Real)</div>
                <div class="time-value">${participant.chipResult}</div>
                <div class="time-note">Pace: ${pace}/km</div>
            </div>
            <div class="time-card">
                <div class="time-label">Gun Time (Official)</div>
                <div class="time-value">${participant.gunResult}</div>
                <div class="time-note">+${timeDiff}s start delay</div>
            </div>
        </div>

        <div class="rankings-grid">
            <div class="ranking-card">
                <div class="ranking-title">Overall Ranking</div>
                <div class="ranking-value">${participant.overallRank} / ${raceData.length}</div>
                <div class="percentile">Top ${overallPercentile}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${overallPercentile}%"></div>
                </div>
            </div>

            <div class="ranking-card">
                <div class="ranking-title">Gender Ranking (${participant.gender})</div>
                <div class="ranking-value">${participant.genderRank} / ${genderCount}</div>
                <div class="percentile">Top ${genderPercentile}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${genderPercentile}%"></div>
                </div>
            </div>

            <div class="ranking-card">
                <div class="ranking-title">Category Ranking (${participant.category})</div>
                <div class="ranking-value">${participant.categoryRank} / ${categoryCount}</div>
                <div class="percentile">Top ${categoryPercentile}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${categoryPercentile}%"></div>
                </div>
            </div>
        </div>

        <div class="action-buttons">
            <button class="action-btn" onclick="printResults()" aria-label="Print results">
                🖨️ Print
            </button>
            <button class="action-btn" onclick="shareResults(${participant.bib})" aria-label="Share results">
                🔗 Share Link
            </button>
            <button class="action-btn secondary" onclick="clearSearch()" aria-label="Clear search">
                ✕ Clear
            </button>
        </div>
    `;

    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Display overall statistics
function displayOverallStats(dataToUse = raceData) {
    const statsContainer = document.getElementById('overallStats');

    const finishers = dataToUse.filter(p => p.chipResult).length;
    const maleCount = dataToUse.filter(p => p.gender === 'M').length;
    const femaleCount = dataToUse.filter(p => p.gender === 'F').length;

    const times = dataToUse.map(p => timeToSeconds(p.chipResult)).filter(t => t !== null);
    const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
    const sortedTimes = times.sort((a, b) => a - b);
    const medianTime = sortedTimes[Math.floor(sortedTimes.length / 2)];
    const fastestTime = sortedTimes[0];
    const slowestTime = sortedTimes[sortedTimes.length - 1];

    const nationalities = [...new Set(dataToUse.map(p => p.nationality))].length;

    statsContainer.innerHTML = `
        <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-value">${finishers}</div>
            <div class="stat-label">Total Finishers</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">♂️</div>
            <div class="stat-value">${maleCount}</div>
            <div class="stat-label">Male</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">♀️</div>
            <div class="stat-value">${femaleCount}</div>
            <div class="stat-label">Female</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">⏱️</div>
            <div class="stat-value">${secondsToTime(Math.floor(avgTime))}</div>
            <div class="stat-label">Average Time</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-value">${secondsToTime(medianTime)}</div>
            <div class="stat-label">Median Time</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🏆</div>
            <div class="stat-value">${secondsToTime(fastestTime)}</div>
            <div class="stat-label">Fastest Time</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🐢</div>
            <div class="stat-value">${secondsToTime(slowestTime)}</div>
            <div class="stat-label">Slowest Time</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🌍</div>
            <div class="stat-value">${nationalities}</div>
            <div class="stat-label">Countries</div>
        </div>
    `;
}

// Create charts
function createCharts() {
    // Destroy existing charts before creating new ones
    Object.values(charts).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    });
    charts = {};

    createTimeDistributionChart();
    createCategoryChart();
    createGenderChart();
    createNationalityChart();
}

// Update charts with filtered data
function updateCharts(dataToUse) {
    // Destroy existing charts
    Object.values(charts).forEach(chart => chart.destroy());
    charts = {};

    // Recreate charts with filtered data
    createTimeDistributionChart(dataToUse);
    createCategoryChart(dataToUse);
    createGenderChart(dataToUse);
    createNationalityChart(dataToUse);
}

// Time distribution chart
function createTimeDistributionChart(dataToUse = raceData) {
    const ctx = document.getElementById('timeDistChart').getContext('2d');
    const times = dataToUse.map(p => timeToSeconds(p.chipResult)).filter(t => t !== null);

    // Create histogram bins (15-minute intervals)
    const bins = {};
    times.forEach(time => {
        const bin = Math.floor(time / 900) * 15; // 15-minute bins in minutes
        bins[bin] = (bins[bin] || 0) + 1;
    });

    const labels = Object.keys(bins).sort((a, b) => a - b);
    const data = labels.map(label => bins[label]);

    charts.timeDistChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.map(l => `${Math.floor(l / 60)}:${(l % 60).toString().padStart(2, '0')}`),
            datasets: [{
                label: 'Number of Finishers',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Finishers'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time (HH:MM)'
                    }
                }
            }
        }
    });
}

// Category performance chart
function createCategoryChart(dataToUse = raceData) {
    const ctx = document.getElementById('categoryChart').getContext('2d');

    // Group by category and calculate average times
    const categoryStats = {};
    dataToUse.forEach(p => {
        if (!categoryStats[p.category]) {
            categoryStats[p.category] = { times: [], count: 0 };
        }
        const time = timeToSeconds(p.chipResult);
        if (time) {
            categoryStats[p.category].times.push(time);
            categoryStats[p.category].count++;
        }
    });

    // Calculate averages and sort by average time
    const categories = Object.keys(categoryStats).map(cat => ({
        name: cat,
        avgTime: categoryStats[cat].times.reduce((a, b) => a + b, 0) / categoryStats[cat].times.length,
        count: categoryStats[cat].count
    })).sort((a, b) => a.avgTime - b.avgTime).slice(0, 10);

    charts.categoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categories.map(c => `${c.name} (${c.count})`),
            datasets: [{
                label: 'Average Time (minutes)',
                data: categories.map(c => Math.floor(c.avgTime / 60)),
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Average Time (minutes)'
                    }
                }
            }
        }
    });
}

// Gender distribution chart
function createGenderChart(dataToUse = raceData) {
    const ctx = document.getElementById('genderChart').getContext('2d');

    const maleCount = dataToUse.filter(p => p.gender === 'M').length;
    const femaleCount = dataToUse.filter(p => p.gender === 'F').length;

    charts.genderChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Male', 'Female'],
            datasets: [{
                data: [maleCount, femaleCount],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 99, 132, 0.6)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Nationality chart
function createNationalityChart(dataToUse = raceData) {
    const ctx = document.getElementById('nationalityChart').getContext('2d');

    const nationalityCounts = {};
    dataToUse.forEach(p => {
        nationalityCounts[p.nationality] = (nationalityCounts[p.nationality] || 0) + 1;
    });

    const topNationalities = Object.entries(nationalityCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    charts.nationalityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topNationalities.map(n => n[0]),
            datasets: [{
                label: 'Participants',
                data: topNationalities.map(n => n[1]),
                backgroundColor: 'rgba(153, 102, 255, 0.6)',
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Participants'
                    }
                }
            }
        }
    });
}

// Render leaderboard
function renderLeaderboard(type = 'overall', dataToUse = raceData) {
    const container = document.getElementById('leaderboardTable');

    let data = [...dataToUse];
    if (type === 'male') {
        data = data.filter(p => p.gender === 'M');
    } else if (type === 'female') {
        data = data.filter(p => p.gender === 'F');
    }

    // Sort by overall rank
    data = data.sort((a, b) => a.overallRank - b.overallRank).slice(0, 50);

    let html = `
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Bib</th>
                    <th>Name</th>
                    <th>Gender</th>
                    <th>Category</th>
                    <th>Nationality</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
    `;

    data.forEach((p, idx) => {
        const medal = idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : '';
        html += `
            <tr class="${idx < 3 ? 'podium-row' : ''}">
                <td>${medal} ${p.overallRank}</td>
                <td>${p.bib}</td>
                <td>${p.firstname} ${p.lastname}</td>
                <td>${p.gender}</td>
                <td>${p.category}</td>
                <td>${p.nationality}</td>
                <td>${p.chipResult}</td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

// Apply filters
function applyFilters() {
    const gender = document.getElementById('genderFilter').value;
    const category = document.getElementById('categoryFilter').value;
    const nationality = document.getElementById('nationalityFilter').value;

    filteredData = raceData.filter(p => {
        if (gender !== 'all' && p.gender !== gender) return false;
        if (category !== 'all' && p.category !== category) return false;
        if (nationality !== 'all' && p.nationality !== nationality) return false;
        return true;
    });

    // Show filter status
    const filterStatus = document.getElementById('filterStatus');
    const activeFilters = [];
    if (gender !== 'all') activeFilters.push(`Gender: ${gender}`);
    if (category !== 'all') activeFilters.push(`Category: ${category}`);
    if (nationality !== 'all') activeFilters.push(`Nationality: ${nationality}`);

    if (activeFilters.length > 0) {
        filterStatus.innerHTML = `<strong>Active Filters:</strong> ${activeFilters.join(' | ')} <span class="filter-count">(${filteredData.length} participants)</span>`;
        filterStatus.classList.remove('hidden');
    } else {
        filterStatus.classList.add('hidden');
    }

    // Update statistics with filtered data
    displayOverallStats(filteredData);

    // Update charts with filtered data
    updateCharts(filteredData);

    // Update leaderboard
    const activeTab = document.querySelector('.tab-btn.active').dataset.tab;
    renderLeaderboard(activeTab, filteredData);

    // Update URL with filters
    updateUrlWithCurrentState();
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('searchBtn').addEventListener('click', searchByBib);
    document.getElementById('nameSearchBtn').addEventListener('click', searchByName);
    document.getElementById('clearSearchBtn').addEventListener('click', clearSearch);

    document.getElementById('bibSearch').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchByBib();
    });

    document.getElementById('nameSearch').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchByName();
    });

    document.getElementById('genderFilter').addEventListener('change', applyFilters);
    document.getElementById('categoryFilter').addEventListener('change', applyFilters);
    document.getElementById('nationalityFilter').addEventListener('change', applyFilters);

    // Leaderboard tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderLeaderboard(btn.dataset.tab);
        });
    });

    // Keyboard navigation for accessibility
    document.addEventListener('keydown', (e) => {
        // ESC to clear search
        if (e.key === 'Escape') {
            const resultsSection = document.getElementById('participantResults');
            if (!resultsSection.classList.contains('hidden')) {
                clearSearch();
            }
        }
    });
}

// Handle race selector buttons
function setupRaceSelector() {
    const raceButtons = document.querySelectorAll('.race-btn');
    raceButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            // Update active button
            raceButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Get race info
            const raceFile = btn.dataset.file;
            currentRaceName = btn.dataset.race;

            // Hide participant results
            document.getElementById('participantResults').classList.add('hidden');

            // Update URL with just race parameter (clear bib)
            setMultipleUrlParameters({ race: currentRaceName });

            // Load new race data
            await loadRaceData(raceFile);
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    setupRaceSelector();
    setupEventListeners();

    // Check for URL parameters to determine initial state
    const urlRace = getUrlParameter('race');
    const urlGender = getUrlParameter('gender');
    const urlCategory = getUrlParameter('category');
    const urlNationality = getUrlParameter('nationality');

    // Set race from URL if provided
    if (urlRace) {
        currentRaceName = urlRace;
        currentRaceFile = getRaceFile(urlRace);

        // Update active race button
        document.querySelectorAll('.race-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.race === urlRace) {
                btn.classList.add('active');
            }
        });
    }

    // Load the race data (will handle bib parameter after loading)
    loadRaceData(currentRaceFile).then(() => {
        // Apply filters from URL if provided
        if (urlGender || urlCategory || urlNationality) {
            if (urlGender) document.getElementById('genderFilter').value = urlGender;
            if (urlCategory) document.getElementById('categoryFilter').value = urlCategory;
            if (urlNationality) document.getElementById('nationalityFilter').value = urlNationality;
            applyFilters();
        }
    });
});
