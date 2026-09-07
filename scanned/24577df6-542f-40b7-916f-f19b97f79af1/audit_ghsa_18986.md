# [M] OpenMage vulnerable to XSS in Admin Notifications

## Summary
Severity: Medium
Advisory: GHSA-qv78-c8hc-438r
CVE: CVE-2025-64174
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:A/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-11-03
Source: https://github.com/advisories/GHSA-qv78-c8hc-438r
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=0 <20.16.0

## Details
### Summary
OpenMage versions v20.15.0 and earlier are affected by a stored Cross-Site Scripting (XSS) vulnerability that could be abused by an admin with direct database access or the admin notification feed source to inject malicious scripts into vulnerable fields. Malicious JavaScript may be executed in a victim’s browser when they browse to the page containing the vulnerable field.

### Details
Unescaped translation strings and URLs are printed into contexts inside `app/code/core/Mage/Adminhtml/Block/Notification/Grid/Renderer/Actions.php`. A malicious translation or polluted data can inject script. 
- Link labels use __() without escaping.
- ’deleteConfirm()’ embeds a message without escaping.

### PoC
1. Add XSS to admin locale (e.g. app/locale/en_US/local.csv):
    ```
    "Read Details","<img src=x onerror=alert(123)>"
    "Mark as Read","<script>alert(123)</script>"
    ```
2. Flush Cache. Make sure locale is set to en_US.
3. Add any admin notification (e.g. via test.php)
     ```
    <?php
    require 'app/Mage.php';
    Mage::app('admin');
    Mage::getModel('adminnotification/inbox')->setData([
        'severity'  => Mage_AdminNotification_Model_Inbox::SEVERITY_NOTICE,
        'date_added' => now(),
        'title' => 'XSS renderer test',
        'description' => 'Testing actions renderer',
        'url' => 'https://example.com', // makes the "Read Details" link appear
        'is_read' => 0, // makes the "Mark as Read" link appear
        'is_remove' => 0,
    ])->save();
    ```
4. Open Admin → System → Notifications → Inbox.
5. Profit.

### Impact
The vulnerability is only exploitable by an attacker with administrative or translation privileges. Malicious JavaScript may be executed in a victim’s browser when they browse to the admin page containing the vulnerable fields.

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-qv78-c8hc-438r
- https://nvd.nist.gov/vuln/detail/CVE-2025-64174
- https://github.com/OpenMage/magento-lts/commit/9d604f5489851c54a96fca31b0e13c414b0fb20a
- https://github.com/OpenMage/magento-lts
