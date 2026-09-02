### Title
`Oauth.begin_auth` builds the OAuth authorization redirect from an unsanitized `shop` parameter, unlike every other entry point in the gem - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` takes the caller-supplied `shop:` argument and interpolates it directly into the authorization redirect URL via `auth_base_uri(shop)`, with no call to `Utils::ShopValidator.sanitize!` [1](#0-0) . Every other credential-issuing flow in the gem (`token_exchange.rb`, `client_credentials.rb`, `refresh_token.rb`) routes the shop value through `ShopValidator` before trusting it, per the `ShopValidator` usage found in those files. This asymmetry means the very first hop of OAuth — the one that decides which host receives the app's `client_id`, `scope`, `redirect_uri`, and CSRF `state` nonce — is the one hop left unguarded.

### Finding Description
`begin_auth` is documented and typically invoked with a `shop` value taken straight from request input (the docs example reads it from `request.headers["Shop"]`) [2](#0-1) . That value is passed unchanged into `auth_base_uri`:
```
def auth_base_uri(shop)
  return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
  ...
end
``` [1](#0-0) 

`begin_auth` then builds the full authorize URL as `auth_base_uri(shop) + "/oauth/authorize?#{query_string}"`, where `query_string` contains `client_id`, `scope`, `redirect_uri`, and the freshly generated `state` nonce, and returns it alongside a `SessionCookie` whose value is that same `state` [3](#0-2) .

Compare this to `Utils::ShopValidator.sanitize!`, which exists specifically to prevent an attacker-supplied `shop` string from resolving to anything other than a `TRUSTED_SHOPIFY_DOMAINS` suffix (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`), rejecting look-alike and userinfo-embedded domains such as `test-shop.notmyshopify.com` or `shop.myshopify.com@evil.com` [4](#0-3) . That guard is applied in `token_exchange.rb`, `client_credentials.rb`, and `refresh_token.rb`, but `begin_auth`'s `auth_base_uri` never calls it, so the equality the rest of the gem enforces — *host that receives the OAuth query params == a domain the merchant actually controls* — is broken specifically on this path.

### Impact Explanation
An attacker who can influence the `shop` value passed into `begin_auth` (e.g. via a query/header-derived login route, as shown in the gem's own docs example) can cause the app to redirect the victim's browser to an attacker-controlled host with the app's `client_id`, requested `scope`, `redirect_uri`, and the OAuth CSRF `state` nonce in the URL, while the same `state` value is written into the victim's session cookie. The attacker's server, now in possession of the correct `state`/cookie pairing and knowing the app's legitimate `redirect_uri`, can drive the victim to complete an OAuth authorization against a shop the attacker controls (or fabricate a callback), causing the app to bind the victim's browser session to the attacker's shop/access token — a forced OAuth completion / session-fixation scenario. No `client_secret` is exposed here (that is only sent later, and only to Shopify's own domain, in `validate_auth_callback`), so the credential itself is safe, but the authorization flow's identity binding (host receiving the OAuth handshake == a Shopify-trusted domain) is not enforced at this entry point the way it is everywhere else.

### Likelihood Explanation
Exploitability depends entirely on whether the host application passes attacker-influenced input into `begin_auth`'s `shop:` parameter without its own validation. The gem's own documentation demonstrates exactly that pattern (`shop = request.headers["Shop"]`), and the gem provides `ShopValidator.sanitize!` as the intended defense-in-depth for this exact input — but does not apply it inside `begin_auth`. Because the other three OAuth-adjacent flows in this same gem do call `ShopValidator`, this looks like an inconsistency/oversight rather than an intentional design choice, making it a reasonably likely gap for any integrator who does not independently sanitize `shop` before calling `begin_auth`.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop, myshopify_domain: Context.myshopify_domain)` (or the sanitize helper used by `token_exchange`/`client_credentials`/`refresh_token`) at the top of `begin_auth`, before the value reaches `auth_base_uri`, so that all OAuth entry points enforce the same trusted-domain invariant.

### Proof of Concept
1. Host application wires an unauthenticated route to `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")`, mirroring the pattern shown in `docs/usage/oauth.md` [5](#0-4) .
2. Attacker sends the victim a link to `.../login?shop=attacker-controlled.evil.example`.
3. `begin_auth` builds `auth_route = "https://attacker-controlled.evil.example/admin/oauth/authorize?client_id=...&state=<nonce>&redirect_uri=https://legit-app.com/auth/callback&..."` and a `SessionCookie` with the same `<nonce>` [3](#0-2) [1](#0-0) .
4. Victim's browser is redirected to the attacker's server (instead of `*.myshopify.com`), leaking `client_id`, `scope`, `redirect_uri`, and `state` to the attacker, while the victim's cookie jar now holds that same `state` value — setting up a forced-completion / fixation attack against `legit-app.com/auth/callback`.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L36-52)
```ruby
          state = SecureRandom.alphanumeric(NONCE_LENGTH)

          cookie = SessionCookie.new(value: state, expires: Time.now + 60)

          query = {
            client_id: ShopifyAPI::Context.api_key,
            scope: scope.to_s,
            redirect_uri: "#{ShopifyAPI::Context.host}#{redirect_path}",
            state: state,
            "grant_options[]": is_online ? "per-user" : "",
          }

          query_string = URI.encode_www_form(query)
          auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"

          { auth_route: auth_route, cookie: cookie }
        end
```

**File:** lib/shopify_api/auth/oauth.rb (L117-128)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")

          # For first-party apps in development only, we leverage DevServer to build the admin base URI
          admin_web = T.unsafe(Object.const_get("DevServer")) # rubocop:disable Sorbet/ConstantsFromStrings
            .new("admin-web")
          admin_host = admin_web.host!(nonstandard_host_prefix: "admin")
          shop_name = shop.split(".").first

          "https://#{admin_host}/store/#{shop_name}"
        end
```

**File:** docs/usage/oauth.md (L181-199)
```markdown
  def login
    shop = request.headers["Shop"]

    # Builds the authorization URL route to redirect the user to
    auth_response = ShopifyAPI::Auth::Oauth.begin_auth(shop: domain, redirect_path: "/auth/callback")

    # Store the authorization cookie
    cookies[auth_response[:cookie].name] = {
      expires: auth_response[:cookie].expires,
      secure: true,
      http_only: true,
      value: auth_response[:cookie].value
    }

    # Redirect the user to "auth_response[:auth_route]" to allow user to grant the app permission
    # This will lead the user to the Shopify Authorization page
    head 307
    response.set_header("Location", auth_response[:auth_route])
  end
```

**File:** lib/shopify_api/utils/shop_validator.rb (L9-64)
```ruby
      TRUSTED_SHOPIFY_DOMAINS = T.let(
        [
          "shopify.com",
          "myshopify.io",
          "myshopify.com",
          "spin.dev",
          "shop.dev",
        ].freeze,
        T::Array[String],
      )

      class << self
        extend T::Sig

        sig do
          params(
            shop_domain: String,
            myshopify_domain: T.nilable(String),
          ).returns(T.nilable(String))
        end
        def sanitize_shop_domain(shop_domain, myshopify_domain: nil)
          uri = uri_from_shop_domain(shop_domain, myshopify_domain)
          return nil if uri.nil? || uri.host.nil? || uri.host.empty?

          trusted_domains(myshopify_domain).each do |trusted_domain|
            host = T.cast(uri.host, String)
            uri_domain = uri.domain
            next if uri_domain.nil?

            no_shop_name_in_subdomain = host == trusted_domain
            from_trusted_domain = trusted_domain == uri_domain

            if unified_admin?(uri) && from_trusted_domain
              return myshopify_domain_from_unified_admin(uri)
            end
            return nil if no_shop_name_in_subdomain || host.empty?
            return host if from_trusted_domain
          end
          nil
        end

        sig do
          params(
            shop: String,
            myshopify_domain: T.nilable(String),
          ).returns(String)
        end
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
        end
```
