# URL Parameters Guide

The Run in Lyon web application now supports comprehensive URL parameters for sharing and bookmarking specific views.

## 📋 Supported Parameters

### Required Parameters
- `race` - The race type (values: `10k`, `21k`, `42k`)

### Optional Parameters
- `bib` - Participant bib number (displays specific participant results)
- `gender` - Filter by gender (values: `M`, `F`, `all`)
- `category` - Filter by age category (values vary by race)
- `nationality` - Filter by nationality (values vary by race)

## 🔗 Example URLs

### View Specific Participant
```
http://localhost:8000/web/?race=21k&bib=12005
```
Opens the Half Marathon (21K) and displays results for participant with bib #12005.

### View Race with Filters
```
http://localhost:8000/web/?race=42k&gender=F&category=Senior
```
Opens the Marathon (42K) filtered to show only Female participants in the Senior category.

### Complete Example
```
http://localhost:8000/web/?race=10k&bib=100&gender=M&category=Master%201
```
Opens the 10K race, shows participant #100, with filters applied for Male participants in Master 1 category.

## 🎯 How It Works

### Automatic URL Updates
The URL automatically updates when you:
1. **Switch races** - Adds `?race=10k` (or 21k, 42k)
2. **Search for participant** - Adds `&bib=12005`
3. **Apply filters** - Adds `&gender=M&category=Senior&nationality=FRA`

### Share Link Feature
When you click "🔗 Share Link":
- Copies the complete current URL to clipboard
- Includes race type, participant bib, and all active filters
- Perfect for sharing exact view with others

### Page Load Behavior
When you open a URL with parameters:
1. ✅ Loads the correct race data (10K, 21K, or 42K)
2. ✅ Updates race selector button to show active race
3. ✅ Finds and displays the participant (if bib parameter provided)
4. ✅ Applies all filters (gender, category, nationality)
5. ✅ Shows the exact same view as when the link was created

## 💡 Use Cases

### For Participants
Share your race results:
```
"Check out my Half Marathon results!"
http://localhost:8000/web/?race=21k&bib=5432
```

### For Coaches
Share filtered views:
```
"Here are all our club's participants in the Marathon"
http://localhost:8000/web/?race=42k&nationality=FRA
```

### For Analysis
Bookmark specific views:
```
"Top Female Seniors in 10K"
http://localhost:8000/web/?race=10k&gender=F&category=Senior
```

## 🔄 URL Persistence

- URLs are updated in browser history using `pushState`
- Browser back/forward buttons work correctly
- Refreshing the page maintains your current view
- Bookmarks save the exact state

## 🛠️ Technical Details

### Parameter Format
- Uses standard URL query string format
- Parameters separated by `&`
- Special characters are URL-encoded
- Case-sensitive for some values

### Default Behavior
If no parameters provided:
- Loads 10K race by default
- Shows overview statistics
- No filters applied
- No participant selected

### Invalid Parameters
If invalid parameters are provided:
- Invalid race → defaults to 10K
- Invalid bib → shows error toast notification
- Invalid filters → treated as "all"

## 📱 Browser Compatibility

Works in all modern browsers:
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers

## 🎨 Example Scenarios

### Scenario 1: Share Your Results
1. Search for your bib number
2. Click "🔗 Share Link"
3. Send link to friends
4. They see your exact results when opening the link

### Scenario 2: Bookmark Filtered View
1. Select Half Marathon race
2. Filter to your country
3. Bookmark the page
4. Opening bookmark shows same filtered view

### Scenario 3: Direct Access
1. Receive link from friend: `?race=42k&bib=999`
2. Open link
3. Marathon race loads automatically
4. Participant #999 results displayed

---

**Note**: Replace `http://localhost:8000` with your actual domain when deploying.
