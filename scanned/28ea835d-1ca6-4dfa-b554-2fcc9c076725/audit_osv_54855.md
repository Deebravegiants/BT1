# [H] CVE-2024-53920

## Summary
Severity: High
Advisory: CVE-2024-53920
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-11-27
Source: https://osv.dev/vulnerability/CVE-2024-53920
Type: osv

## Details
In elisp-mode.el in GNU Emacs before 30.1, a user who chooses to invoke elisp-completion-at-point (for code completion) on untrusted Emacs Lisp source code can trigger unsafe Lisp macro expansion that allows attackers to execute arbitrary code. (This unsafe expansion also occurs if a user chooses to enable on-the-fly diagnosis that byte compiles untrusted Emacs Lisp source code.)

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00033.html
- https://git.savannah.gnu.org/cgit/emacs.git/tag/?h=emacs-30.0.92
- https://git.savannah.gnu.org/cgit/emacs.git/tree/etc/NEWS?h=emacs-30.1
- https://eshelyaron.com/posts/2024-11-27-emacs-aritrary-code-execution-and-how-to-avoid-it.html
- https://git.savannah.gnu.org/cgit/emacs.git/tree/ChangeLog.4
- https://news.ycombinator.com/item?id=42256409
- https://yhetil.org/emacs/CAFXAjY5f4YfHAtZur1RAqH34UbYU56_t6t2Er0YEh1Sb7-W=hg@mail.gmail.com/
