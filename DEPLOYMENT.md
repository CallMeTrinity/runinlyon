# Deployment Guide

This guide explains how to deploy the Run in Lyon Race Results Explorer to various hosting platforms.

## 📋 Pre-Deployment Checklist

Before deploying, ensure:
- ✅ All race data files are in the `data/` directory
- ✅ Web application files are in the `web/` directory
- ✅ `.htaccess` file is in the root directory
- ✅ Test locally using `python start_server.py`

## 🌐 Apache Web Server Deployment

### Requirements
- Apache 2.x web server
- `mod_rewrite` enabled
- `mod_headers` enabled (optional, for caching/security)
- `mod_deflate` enabled (optional, for compression)

### Deployment Steps

1. **Upload Files**
   ```bash
   # Upload entire project directory via FTP/SFTP
   # or use git clone on the server
   git clone <your-repo-url> /var/www/runinlyon
   ```

2. **Enable Apache Modules**
   ```bash
   sudo a2enmod rewrite
   sudo a2enmod headers
   sudo a2enmod deflate
   sudo a2enmod expires
   sudo systemctl restart apache2
   ```

3. **Configure Apache Virtual Host**

   Edit your Apache configuration (e.g., `/etc/apache2/sites-available/runinlyon.conf`):

   ```apache
   <VirtualHost *:80>
       ServerName runinlyon.yourdomain.com
       DocumentRoot /var/www/runinlyon

       <Directory /var/www/runinlyon>
           Options -Indexes +FollowSymLinks
           AllowOverride All
           Require all granted
       </Directory>

       ErrorLog ${APACHE_LOG_DIR}/runinlyon-error.log
       CustomLog ${APACHE_LOG_DIR}/runinlyon-access.log combined
   </VirtualHost>
   ```

4. **Enable Site and Restart**
   ```bash
   sudo a2ensite runinlyon
   sudo systemctl restart apache2
   ```

5. **Test Deployment**
   - Visit: `http://runinlyon.yourdomain.com`
   - Should redirect to `web/index.html` automatically
   - Test URL parameters: `?race=10k&bib=1`

### How .htaccess Works

The `.htaccess` file in the root directory handles:
- **Root redirect**: `/` → `/web/`
- **Clean URLs**: Requests automatically routed to `web/` directory
- **CORS**: Allows JSON data loading
- **Compression**: Gzip compression for faster loading
- **Caching**: Browser caching for static assets
- **Security**: Headers to prevent common attacks

## 🔒 HTTPS/SSL Setup

For production, always use HTTPS:

### Using Let's Encrypt (Free SSL)

```bash
# Install certbot
sudo apt install certbot python3-certbot-apache

# Get certificate
sudo certbot --apache -d runinlyon.yourdomain.com

# Auto-renewal is set up automatically
# Test renewal with:
sudo certbot renew --dry-run
```

Your Apache config will be automatically updated to use HTTPS.

## 🚀 Alternative Deployment Options

### 1. Shared Hosting (cPanel/Plesk)

1. **Upload via File Manager or FTP**
   - Upload entire project to `public_html/` or subdirectory
   - Ensure `.htaccess` is uploaded (might be hidden)

2. **Set Permissions**
   - Files: 644
   - Directories: 755
   - `.htaccess`: 644

3. **Test**
   - Visit: `http://yourdomain.com/`
   - Should automatically show the race results explorer

### 2. Static Hosting (GitHub Pages, Netlify, Vercel)

These platforms don't support `.htaccess`, so you need to adjust:

#### GitHub Pages
```bash
# Create a copy of index.html in root
cp web/index.html index.html

# Update paths in root index.html
# Change: ../data/639.json → data/639.json
# Change: styles.css → web/styles.css
# Change: app.js → web/app.js

# Commit and push
git add index.html
git commit -m "Add root index for GitHub Pages"
git push

# Enable GitHub Pages in repository settings
# Choose 'main' branch, root directory
```

#### Netlify
Create `netlify.toml` in root:
```toml
[[redirects]]
  from = "/"
  to = "/web/index.html"
  status = 200

[[redirects]]
  from = "/*"
  to = "/web/:splat"
  status = 200

[[headers]]
  for = "/*.json"
  [headers.values]
    Access-Control-Allow-Origin = "*"
```

Deploy:
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod
```

#### Vercel
Create `vercel.json` in root:
```json
{
  "rewrites": [
    { "source": "/", "destination": "/web/index.html" },
    { "source": "/(.*)", "destination": "/web/$1" }
  ],
  "headers": [
    {
      "source": "/(.*).json",
      "headers": [
        { "key": "Access-Control-Allow-Origin", "value": "*" }
      ]
    }
  ]
}
```

Deploy:
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### 3. Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM httpd:2.4-alpine

# Copy project files
COPY . /usr/local/apache2/htdocs/

# Enable rewrite module
RUN sed -i '/LoadModule rewrite_module/s/^#//g' /usr/local/apache2/conf/httpd.conf

# Allow .htaccess
RUN sed -i 's/AllowOverride None/AllowOverride All/g' /usr/local/apache2/conf/httpd.conf

EXPOSE 80
```

Build and run:
```bash
docker build -t runinlyon .
docker run -d -p 80:80 runinlyon
```

## 🧪 Testing Deployment

After deployment, test these URLs:

1. **Root URL**: `http://yourdomain.com/`
   - Should load the race results explorer
   - Default to 10K race

2. **Direct Access**: `http://yourdomain.com/web/`
   - Should also work

3. **URL Parameters**: `http://yourdomain.com/?race=21k&bib=100`
   - Should load Half Marathon
   - Should display participant #100

4. **JSON Loading**: Check browser console
   - Should successfully load `data/639.json`
   - No CORS errors

5. **Filters**: Test gender/category/nationality filters
   - URL should update with parameters

6. **Share Link**: Click share button
   - Should copy complete URL with all parameters

## 🔧 Troubleshooting

### Issue: "404 Not Found" on root URL
**Solution**: Ensure `.htaccess` is uploaded and `mod_rewrite` is enabled

### Issue: JSON files won't load (CORS error)
**Solution**:
- Check CORS headers in `.htaccess`
- Verify `mod_headers` is enabled
- Check browser console for specific error

### Issue: URLs with parameters don't work
**Solution**:
- Ensure `mod_rewrite` is enabled
- Check `.htaccess` RewriteEngine is On
- Verify AllowOverride is set to All in Apache config

### Issue: Styles/Scripts not loading
**Solution**:
- Check file paths in HTML
- Verify all files uploaded correctly
- Check browser console for 404 errors

### Issue: Large JSON files slow to load
**Solution**:
- Enable gzip compression (`mod_deflate`)
- Set proper caching headers
- Consider serving from CDN

## 📊 Performance Optimization

### Enable Compression
Already configured in `.htaccess` if `mod_deflate` is enabled.

### Browser Caching
Already configured in `.htaccess` if `mod_expires` is enabled.

### CDN (Optional)
For faster global access, consider using a CDN:
- Cloudflare (Free tier available)
- AWS CloudFront
- Azure CDN

## 🔐 Security Considerations

The `.htaccess` file includes basic security headers:
- X-Frame-Options (prevent clickjacking)
- X-XSS-Protection
- X-Content-Type-Options
- Referrer-Policy

Additional recommendations:
- Always use HTTPS in production
- Keep server software updated
- Regular backups of race data
- Monitor access logs for suspicious activity

## 📱 Mobile Optimization

The app is already mobile-responsive. For best mobile performance:
- Use HTTPS (required for some mobile features)
- Enable compression
- Set proper caching headers

## 🔄 Updating Race Data

To update race data after deployment:

1. **Upload new JSON files** to `data/` directory
2. **Clear browser cache** for users (or update cache headers)
3. **Test** with URL parameters to verify new data loads

## 📞 Support

For deployment issues:
- Check Apache error logs: `/var/log/apache2/error.log`
- Check browser console for JavaScript errors
- Verify file permissions (644 for files, 755 for directories)

---

**Deployment Checklist Summary:**

- [ ] Files uploaded to server
- [ ] `.htaccess` in root directory
- [ ] Apache modules enabled (rewrite, headers, deflate)
- [ ] Virtual host configured (if applicable)
- [ ] HTTPS/SSL certificate installed
- [ ] Root URL tested (redirects to web/)
- [ ] URL parameters tested
- [ ] JSON data loading verified
- [ ] Share link functionality tested
- [ ] Mobile responsiveness checked

**🎉 Your deployment is complete!**
