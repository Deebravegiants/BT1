# [M] syncthing vulnerable to Cross-site Scripting (XSS) in Web GUI

## Summary
Severity: Medium
Advisory: GHSA-9rp6-23gf-4c3h
CVE: CVE-2022-46165
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-9rp6-23gf-4c3h
Type: github-advisory

## Affected
- Go: `github.com/syncthing/syncthing` — affected >=0 <1.23.5

## Details
## Impact

1. A compromised instance with shared folders could sync malicious files which contain arbitrary HTML and JavaScript in the name.
If the owner of another device looks over the shared folder settings and moves the mouse over the latest sync, a script could be executed to change settings for shared folders or add devices automatically.

2. Adding a new device with a malicious name could embed HTML or JavaScript inside parts of the page.

## Risk

As long as trusted devices are used, the risk is low.
Additionally, the web GUI is not used that often in daily use which reduces the likelihood of exploitation.

## Details

### 1. Field "Latest Change"

* Open the web GUI at [http://127.0.0.1:8384/](http://127.0.0.1:8384/).
* Create/Delete a file named ```<img src=a onerror=alert(123)>``` and sync it to the other instance.
* Move your mouse over the latest change to trigger the tooltip.

<img width="834" alt="latest-change" src="https://user-images.githubusercontent.com/9484134/205084362-20a8ec13-a88d-469f-bdf1-e5291c20f4c1.png">

##### Web browser source
```html
<span tooltip="" data-original-title="\&quot;><img src=a onerror=alert(123)> @ 2022-11-30 16:58:43"
    aria-describedby="tooltip409527">
    <!-- ngIf: !folderStats[folder.id].lastFile.deleted --><span translate=""
        translate-value-file="&quot;><img src=a onerror=alert(123)>" ng-if="!folderStats[folder.id].lastFile.deleted"
        class="ng-scope">Updated "&gt;&lt;img src=a onerror=alert(123)&gt;</span>
    <!-- end ngIf: !folderStats[folder.id].lastFile.deleted -->
    <!-- ngIf: folderStats[folder.id].lastFile.deleted -->
</span>
<div class="tooltip fade top in" role="tooltip" id="tooltip409527"
    style="top: 446.033px; left: 318.3px; display: block;">
    <div class="tooltip-arrow" style="left: 50%;"></div>
    <div class="tooltip-inner">\"&gt;<img src="a" onerror="alert(123)"> @ 2022-11-30 16:58:43</div>
</div>
```

##### Corresponding code in the project 

File ````gui/default/index.html````:
```html
<tr ng-if="folder.type != 'sendonly' && folder.type != 'receiveencrypted' && folderStats[folder.id].lastFile && folderStats[folder.id].lastFile.filename">
    <th><span class="fas fa-fw fa-exchange-alt"></span>&nbsp;<span translate>Latest Change</span></th>
    <td class="text-right">
        <span tooltip data-original-title="{{folderStats[folder.id].lastFile.filename}} @ {{folderStats[folder.id].lastFile.at | date:'yyyy-MM-dd HH:mm:ss'}}">
        <span translate translate-value-file="{{folderStats[folder.id].lastFile.filename | basename}}" ng-if="!folderStats[folder.id].lastFile.deleted">Updated {%file%}</span>
        <span translate translate-value-file="{{folderStats[folder.id].lastFile.filename | basename}}" ng-if="folderStats[folder.id].lastFile.deleted">Deleted {%file%}</span>
        </span>
    </td>
</tr>
```

File ````gui/default/syncthing/core/tooltipDirective.js````:  
```javascript
angular.module('syncthing.core')
    .directive('tooltip', function () {
        return {
            restrict: 'A',
            link: function (scope, element, attributes) {
                $(element).tooltip({
                    html: 'true'
                });
            }
        };
    });
```

The attribute ```html``` should not be set to ```true``` or input sanitized.

### 2. Field "Shared With"

* Open the web GUI at [http://127.0.0.1:8384/](http://127.0.0.1:8384/).
* Create a device with the following name ```fedora 1"'><h1>Headline</h1><img src=x><script>alert(1)</script>```.
* Add the device to another instance and share a folder.
* Move your mouse over the malicious device name to trigger the tooltip.
 
<img width="608" alt="shared-with-1" src="https://user-images.githubusercontent.com/9484134/205084172-8cab2d0e-3257-46d5-be81-41fbd7228e0c.png">


##### Web browser source  

```html
<span tooltip="" data-original-title="fedora 1&quot;'><h1>Headline</h1><img src=x><script>alert(1)</script>  "
    ng-bind-html="sharesFolder(folder)" class="ng-binding" aria-describedby="tooltip348410">fedora 1"'&gt;<h1>Headline
    </h1><img src="x"></span>
<div class="tooltip fade top" role="tooltip" id="tooltip348410" style="top: 0px; left: 0px; display: block;">
    <div class="tooltip-arrow" style="left: 50%;"></div>
    <div class="tooltip-inner">fedora 1"'&gt;<h1>Headline</h1><img src="x">
        <script>alert(1)</script>
    </div>
</div>
```

##### Corresponding code in the project 

File ````gui/default/index.html````:

```html
<tr>
    <th><span class="fas fa-fw fa-share-alt"></span>&nbsp;<span translate>Shared With</span></th>
    <td class="text-right">
        <span tooltip data-original-title="{{sharesFolder(folder)}} {{folderHasUnacceptedDevices(folder) ? '<br/>(<sup>1</sup>' + ('The remote device has not accepted sharing this folder.' | translate) + ')' : ''}} {{folderHasPausedDevices(folder) ? '<br/>(<sup>2</sup>' + ('The remote device has paused this folder.' | translate) + ')' : ''}}" ng-bind-html="sharesFolder(folder)"></span>
    </td>
</tr>
```

File ````gui/default/syncthing/core/tooltipDirective.js````:  

```javascript
angular.module('syncthing.core')
    .directive('tooltip', function () {
        return {
            restrict: 'A',
            link: function (scope, element, attributes) {
                $(element).tooltip({
                    html: 'true'
                });
            }
        };
    });
```

The attribute ```html``` should not be set to ```true``` or input sanitized.

##### HTML Injection in "Edit Folder"

<img width="672" alt="shared-with-2" src="https://user-images.githubusercontent.com/9484134/205084067-b33f8536-e350-4de1-86f6-3d4a12a683c3.png">

## References
- https://github.com/syncthing/syncthing/security/advisories/GHSA-9rp6-23gf-4c3h
- https://nvd.nist.gov/vuln/detail/CVE-2022-46165
- https://github.com/syncthing/syncthing/commit/73c52eafb6566435dffd979c3c49562b6d5a4238
- https://github.com/syncthing/syncthing/commit/f5e5af391a6583047c64ef8c51642003a79b75cf
- https://github.com/syncthing/syncthing
- https://github.com/syncthing/syncthing/releases/tag/v1.23.5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IRYGBFJPVBW6PPTETNIBWQJE4HJSA5PJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XEBWSQVGHSTR4ZO7LVVEMPEGMV2DS5XR
