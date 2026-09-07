# [H] Cross-site Scripting (XSS) in DemoBundle/ezdemo bundled VideoJS

## Summary
Severity: High
Advisory: GHSA-jq9q-6p42-qpr7
CWE: CWE-79
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-jq9q-6p42-qpr7
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezdemo-ls-extension` — affected >=5.4.0 <5.4.2.1

## Details
his Security Advisory is about a vulnerability in VideoJS, which is bundled in DemoBundle and the ezdemo legacy extension. Older releases of VideoJS contain an XSS vulnerability in the Flash-based video player. This is bundled in DemoBundle, and in the Legacy "ezdemo" and "ezdemo-ls-extension" extensions. Among the branches still receiving security advisories, only eZ Publish Platform 5.4 and eZ Publish Legacy 5.4 are affected. However, it may be possible to make this software work in newer branches, so please check whether you have it installed even if you're using eZ Platform 1.x or 2.x.

Because DemoBundle / ezdemo are only intended for demo purposes, they are not supported software. For that reason, and given the old age of the software, and manpower issues during the Coronavirus crisis, we are taking the unusual step of simply removing the affected file. This resolves the vulnerability, but also breaks the video playback feature. It may be possible to make it work again by upgrading to a current version of VideoJS, but it is unlikely that we will do this, given the reasons already mentioned.

## References
- https://ezplatform.com/security-advisories/ezsa-2020-003-xss-in-demobundle-ezdemo-bundled-videojs
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezdemo-ls-extension/2020-04-21-1.yaml
- https://github.com/ezsystems/ezdemo-ls-extension
- https://web.archive.org/web/20201024034648/https://ezplatform.com/security-advisories/ezsa-2020-003-xss-in-demobundle-ezdemo-bundled-videojs
