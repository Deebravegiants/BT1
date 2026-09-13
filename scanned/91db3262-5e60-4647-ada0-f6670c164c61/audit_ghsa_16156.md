# [C] LibreNMS has an Authenticated OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-x645-6pf9-xwxw
CVE: CVE-2024-51092
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2024-11-15
Source: https://github.com/advisories/GHSA-x645-6pf9-xwxw
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <24.10.0

## Details
### Summary
An authenticated attacker can create dangerous directory names on the system and alter sensitive configuration parameters through the web portal. Those two defects combined then allows to inject arbitrary OS commands inside `shell_exec()` calls, thus achieving arbitrary code execution.

### Details
#### OS Command Injection
We start by inspecting the file `app/Http/Controllers/AboutController.php`, more particularly the index() method which is executed upon simply visiting the /about page:
```php
public function index(Request $request)
    {
        $version = Version::get();

        return view('about.index', [
            <TRUNCATED>

            'version_webserver' => $request->server('SERVER_SOFTWARE'),
            'version_rrdtool' => Rrd::version(),
            'version_netsnmp' => str_replace('version: ', '', rtrim(shell_exec(Config::get('snmpget', 'snmpget') . ' -V 2>&1'))),

           <TRUNCATED>
        ]);
    }
```

We can see that the `version_netsnmp` key receives a value direclty dependent of a `shell_exec()` call. The argument to this call reflects a configuration parameter with no sanitization. Should an attacker identify a way to alter this parameter, the server is at risk of being compromised.

#### Configuration parameters poisoning
We now focus on the `update()` method of the `SettingsController.php` script. This method is called when the user visits the route `/settings/{key}` via HTTP PUT. The key parameter here is simply the name of the configuration key the user wishes to modify.
```php
public function update(DynamicConfig $config, Request $request, $id)
{
    $value = $request->get('value');

    if (! $config->isValidSetting($id)) {
        return $this->jsonResponse($id, ':id is not a valid setting', null, 400);
    }

    $current = \LibreNMS\Config::get($id);
    $config_item = $config->get($id);

    if (! $config_item->checkValue($value)) {
        return $this->jsonResponse($id, $config_item->getValidationMessage($value), $current, 400);
    }

    if (\LibreNMS\Config::persist($id, $value)) {
        return $this->jsonResponse($id, "Successfully set $id", $value);
    }

    return $this->jsonResponse($id, 'Failed to update :id', $current, 400);
}
```

We can see that some protections are implemented around the configuration parameters by `$config_item->checkValue($value)`, with a format of data being expected depending on the data type of the variable the user wants to modify.
Specifically, the `snmpget` configuration variable expects a valid path to an existing binary on the system.
To summarize : if an attacker finds a valid full-path to a system binary, while that full-path also holds shell metacharacters, then those characters would be interpreted by the `shell_exec()` call defined above and allow for arbitrary command execution.

#### Arbitrary directory creation
When creating a new Device through the "Add Device" page, the server allows the user to send malformed or impossible hostnames and force the data to be stored, with no sanitization being performed on this field.

In the file `app/Jobs/PollDevice.php`, the `initRrdDirectory()` method is responsible for creating a directory named after the Device's hostname. We can see the `mkdir()` call inside the try block:
```php
private function initRrdDirectory(): void
{
    $host_rrd = \Rrd::name($this->device->hostname, '', '');
    if (Config::get('rrd.enable', true) && ! is_dir($host_rrd)) {
        try {
            mkdir($host_rrd);
            Log::info("Created directory : $host_rrd");
        } catch (\ErrorException $e) {
            Eventlog::log("Failed to create rrd directory: $host_rrd", $this->device);
            Log::info($e);
        }
    }
}
```

This method is called by `initDevice()`, which is itself called by the `handle()` method (executed when the job starts).
`\Rrd::name()` simply concatenates a string following the format `<LIBRENMS_INSTALL_DIR>/rrd/<DEVICE_HOSTNAME>`.

#### Summary
With all this, an authenticated attacker can:
- Create a malicious Device with shell metacharacters inside its hostname
- Force the creation of directory containing shell metacharacters through the PollDevice job
- Modify the `snmpget` configuration variable to point to a valid system binary, while also using the directory created in the previous step via a path traversal (i.e: `/path/to/install/dir/rrd/<DEVICE_HOSTNAME>/../../../../../../../bin/ls`)
- Trigger a code execution via the `shell_exec()` call contained in the `AboutController.php` script

#### 

### PoC
For proof of concept, we will create a file located at `/tmp/rce-proof` on the server's filesystem.

Consider the following command : `/usr/bin/touch /tmp/rce-proof`, encoded in base64 (`L3Vzci9iaW4vdG91Y2ggL3RtcC9yY2UtcHJvb2Y=`). This encoding is necesary whenever the command contains '/' characters, as this would otherwise generate invalid directory paths.
Create a new Device with a name that contains the command you wish to execute enclosed in semi-colons, ending with a '3' character:
![librenms-1](https://github.com/user-attachments/assets/a242fc1a-f04a-4df9-901e-abcc5f14af14)

Be careful to tick the "Force Add" option, otherwise the request will be rejected. Click add:
![librenms-2](https://github.com/user-attachments/assets/84e0d853-1418-44aa-870b-4259adba27f8)

A directory matching the hostname of the Device will be created whenever a PollDevice job is launched. For the purpose of the demonstration, we will be triggering this manually with artisan:
![librenms-4](https://github.com/user-attachments/assets/ce4061ef-6cb6-4847-a229-1417091048f5)

We can confirm that this directory indeed exists on the system:
![librenms-5](https://github.com/user-attachments/assets/79f912c6-f200-47d2-b950-d46636dc30ef)

We can now update the `snmpget` parameter value to point to any binary on the system, making sure that the specified path includes the directory that was just created:
![librenms-13](https://github.com/user-attachments/assets/4b49c2db-c716-41ae-b668-ff6bf3d5d8de)

Visiting the `/about` page will trigger the payload, then we can check that our code was indeed executed:
![librenms-10](https://github.com/user-attachments/assets/8fcf0838-50b5-47e0-85d5-0892d9909c76)


### Impact
Server takeover

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-x645-6pf9-xwxw
- https://nvd.nist.gov/vuln/detail/CVE-2024-51092
- https://github.com/librenms/librenms
- https://raw.githubusercontent.com/rapid7/metasploit-framework/master/modules/exploits/linux/http/librenms_authenticated_rce_cve_2024_51092.rb
