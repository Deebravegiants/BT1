### Title
Weak password complexity policy allows trivially guessable passwords (sequential/repeated characters) - ([File: core/utils/password.go])

### Summary
Chainlink's centralized password validator, `utils.VerifyPasswordComplexity`, only enforces password length (≥16 chars), absence of leading/trailing whitespace, and disallows a caller-supplied substring (typically the user's own email). It performs no check against low-entropy patterns such as repeated characters, sequential digits/letters, or common keyboard patterns. As a result, any authenticated user can set a "strong-looking" but trivially guessable password (e.g. all-same-character or sequential strings padded to 16+ characters), analogous to the reported weak-password issue (`0123456789`, `000000`, `aaaaaa`, `abcdef`), as long as it satisfies the length floor.

### Finding Description
The single point of password validation logic is: [1](#0-0) 

It only checks:
1. Leading/trailing whitespace [2](#0-1) 
2. Minimum length of 16 characters [3](#0-2) 
3. A caller-provided disallowed substring (e.g. the user's email) [4](#0-3) 

There is no entropy, character-class diversity, or pattern-repetition/sequence check. This function is the sole gate used when a user changes their own password via the self-service endpoint: [5](#0-4) 

Any authenticated user, regardless of role (`view`, `run`, `edit`, `admin`), can call this endpoint to set their own password and is only subject to the weak checks in `VerifyPasswordComplexity`. Consequently, values like `aaaaaaaaaaaaaaaa` (16 identical characters), `0123456789012345` (16 sequential digits), or `abcdefabcdefabcd` (repeated low-entropy substring) all pass validation, since they satisfy length and whitespace/email-substring constraints while offering minimal real entropy — directly matching the bug class described in the external report (sequential numbers, simple repeated letter/number combinations).

The same weak check is reused for initial user creation (`clsession.NewUser` → `ValidateAndHashPassword`) [6](#0-5)  and for the `/v2/users` create-user API [7](#0-6) , but I was unable to fully confirm from the index which role is required to call the create-user endpoint (route/role-guard wiring in `core/web/router.go` was not resolved in this investigation), so the strongest confirmed unprivileged-actor path is the self-service `UpdatePassword` endpoint, which every authenticated user of any role can invoke on their own account.

### Impact Explanation
An account (even one created with a policy-compliant initial password) can be degraded to a low-entropy 16+ character password consisting of repeated or sequential characters. This materially increases susceptibility to offline/online brute-force or dictionary-based guessing against that specific account, since the "16-char minimum" gives a false sense of complexity while the actual character-space entropy can be extremely low (e.g., a single repeated character or a fixed sequential pattern).

### Likelihood Explanation
Likelihood is high for any authenticated user (there is no restriction preventing a low-privileged `view` role user from calling `UpdatePassword` on their own account) and requires no special conditions — only knowledge of the current password (already possessed by the account holder) and a JSON PATCH request.

### Recommendation
Extend `VerifyPasswordComplexity` in `core/utils/password.go` to reject low-entropy patterns in addition to the existing length/whitespace/substring checks, e.g.:
- Reject passwords composed of a single repeated character.
- Reject strictly sequential numeric or alphabetic runs (ascending or descending) of significant length.
- Optionally integrate a well-known weak-password/breach-corpus check (e.g., a Have-I-Been-Pwned style dictionary or `zxcvbn`-style entropy estimator) rather than relying purely on length.

### Proof of Concept
1. Authenticate as any existing user (any role).
2. Send `PATCH /v2/user/password` with body:
```json
{"oldPassword": "<current password>", "newPassword": "aaaaaaaaaaaaaaaa"}
```
3. Observe `200 OK` — the request succeeds because `VerifyPasswordComplexity("aaaaaaaaaaaaaaaa", email)` in [1](#0-0)  passes (length 16, no whitespace, no email substring), despite the password having near-zero entropy.
4. Repeat with `"0123456789012345"` (sequential digits) — also succeeds for the same reason, confirming the underlying weak-password-policy gap matching the external report's bug class.

### Citations

**File:** core/utils/password.go (L44-70)
```go
func VerifyPasswordComplexity(password string, disallowedStrings ...string) (merr error) {
	errMsg := ErrMsgHeader
	var stringErrs []string

	if LeadingWhitespace.MatchString(password) || TrailingWhitespace.MatchString(password) {
		stringErrs = append(stringErrs, ErrWhitespace.Error())
	}

	if len(password) < MinRequiredLen {
		stringErrs = append(stringErrs, fmt.Sprintf("password is less than %d characters long", MinRequiredLen))
	}

	for _, s := range disallowedStrings {
		if strings.Contains(strings.ToLower(password), strings.ToLower(s)) {
			stringErrs = append(stringErrs, fmt.Sprintf("password may not contain: %q", s))
		}
	}

	if len(stringErrs) > 0 {
		for _, stringErr := range stringErrs {
			errMsg = fmt.Sprintf("%s	%s\n", errMsg, stringErr)
		}
		merr = errors.New(errMsg)
	}

	return
}
```

**File:** core/web/user_controller.go (L52-80)
```go
func (u *UserController) Create(c *gin.Context) {
	ctx := c.Request.Context()
	type newUserRequest struct {
		Email    string `json:"email"`
		Password string `json:"password"`
		Role     string `json:"role"`
	}

	var request newUserRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	userRole, err := clsession.GetUserRole(request.Role)
	if err != nil {
		jsonAPIError(c, http.StatusBadRequest, err)
		return
	}

	if verr := clsession.ValidateEmail(request.Email); verr != nil {
		jsonAPIError(c, http.StatusBadRequest, verr)
		return
	}

	if verr := utils.VerifyPasswordComplexity(request.Password, request.Email); verr != nil {
		jsonAPIError(c, http.StatusBadRequest, verr)
		return
	}
```

**File:** core/web/user_controller.go (L201-233)
```go
// UpdatePassword changes the password for the current User.
func (u *UserController) UpdatePassword(c *gin.Context) {
	ctx := c.Request.Context()
	var request UpdatePasswordRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	sessionUser, ok := webauth.GetAuthenticatedUser(c)
	if !ok {
		jsonAPIError(c, http.StatusInternalServerError, errors.New("failed to obtain current user from context"))
		return
	}
	user, err := u.App.AuthenticationProvider().FindUser(ctx, sessionUser.Email)
	if err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		u.App.GetLogger().Errorf("failed to obtain current user record: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("unable to update password"))
		return
	}
	if !utils.CheckPasswordHash(request.OldPassword, string(user.HashedPassword)) {
		u.App.GetAuditLogger().Audit(audit.PasswordResetAttemptFailedMismatch, map[string]any{"user": user.Email})
		jsonAPIError(c, http.StatusConflict, errors.New("old password does not match"))
		return
	}
	if err := utils.VerifyPasswordComplexity(request.NewPassword, user.Email); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}
```

**File:** core/sessions/user.go (L68-83)
```go
// ValidateAndHashPassword is the single point of logic for user password validations
func ValidateAndHashPassword(plainPwd string) (string, error) {
	if err := utils.VerifyPasswordComplexity(plainPwd); err != nil {
		return "", pkgerrors.Wrapf(err, "password insufficiently complex:\n%s", utils.PasswordComplexityRequirements)
	}
	if len(plainPwd) > MaxBcryptPasswordLength {
		return "", pkgerrors.Errorf("must enter a password less than %v characters", MaxBcryptPasswordLength)
	}

	pwd, err := utils.HashPassword(plainPwd)
	if err != nil {
		return "", err
	}

	return pwd, nil
}
```
