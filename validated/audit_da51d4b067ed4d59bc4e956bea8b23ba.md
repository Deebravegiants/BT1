## Analysis: Webhook `shop` field is not covered by the HMAC signature

Verified in-scope: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/utils/verifiable_query.rb`.

### Title
Webhook `shop` identity is unauthenticated because the HMAC only covers the raw body, letting a malicious merchant forge cross-tenant webhook attribution - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` verifies solely that the body bytes were signed with the app's shared `api_secret_key`. `Registry.process` then trusts `request.shop` — sourced from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header — and hands it straight to the app's handler as `WebhookMetadata.shop`, with no cryptographic binding between the verified body and the claimed shop.

### Finding Description
- `Request#hmac` and `Request#to_signable_string` are defined at [1](#0-0) , and `to_signable_string` returns only `@raw_body`.
- `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no verification: [2](#0-1) .
- `Utils::HmacValidator.validate` computes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it to the `hmac` header value using `OpenSSL.secure_compare` — this only proves the *body* was signed by holders of `api_secret_key`; the `shop` header is never included in the signed material: [3](#0-2) .
- `Registry.process` calls `Utils::HmacValidator.validate(request)` and, if it passes, immediately constructs `WebhookMetadata` using `request.shop` — the unauthenticated header value — as the shop identity handed to the app's business logic: [4](#0-3) .
- The gem's own documentation instructs app developers to trust `data.shop` as "The shop domain of the webhook" and states that `Registry.process` "will verify the request did indeed come from Shopify," implying the whole payload (including shop attribution) is authenticated: [5](#0-4) [6](#0-5) .

The `api_secret_key` (client secret) is shared across *all* shops that install the app — it is not shop-specific — as seen in the OAuth/HMAC flows that reuse the same `Context.api_secret_key` for every shop: [7](#0-6) . Consequently, any merchant who has installed the app can trigger a legitimately Shopify-signed webhook for their **own** shop (e.g., `orders/create`), capture the raw body + valid HMAC, and replay that exact body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. The HMAC check in `HmacValidator.validate` still passes (it only re-hashes the untouched body), but `Registry.process` will deliver the event to the handler tagged with the attacker-chosen `shop`.

Binding broken (equality that should hold but doesn't):
`shop_bound_by_hmac == shop_delivered_to_handler` — in reality `shop_bound_by_hmac` doesn't exist (not part of the signable string) while `shop_delivered_to_handler = request.shop` is taken from an attacker-controllable header.

### Impact Explanation
Any app that (per the gem's documented pattern) uses `data.shop` to key per-tenant state changes from webhook processing (e.g., syncing orders, updating billing, revoking access, writing to a shop-scoped database row) can be made to apply attacker-supplied webhook data under another merchant's shop identity. This is a cross-tenant confusion/attribution bypass: the gem asserts the shop identity is verified ("did indeed come from Shopify") when it is not cryptographically bound to the signed payload. This satisfies the Critical category of cross-tenant access.

### Likelihood Explanation
Exploitation requires only: (1) being a merchant who has installed the app (no special privilege beyond normal app usage) to generate a validly HMAC-signed webhook body for their own shop, and (2) sending an HTTP request to the app's public webhook endpoint with a forged `shop-domain` header. No access token, `api_secret_key`, or TLS interception is required — the attacker uses their own legitimately-received webhook body. This is fully reachable through the gem's documented public API (`Webhooks::Request.new` + `Registry.process`), not a misuse of undocumented behavior.

### Recommendation
Bind the shop identity into the verified material, or require applications to cross-check `request.shop` against the shop that owns the specific `webhook_id`/subscription (e.g., verify the webhook was registered for that shop before dispatching), rather than trusting the raw header. At minimum, the gem should stop implying header fields are Shopify-authenticated when only the body is HMAC-verified — document that `shop`, `topic`, and `webhook_id` headers are unauthenticated and must be independently cross-validated by the host app against known/registered shops.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; attacker triggers `orders/create` on their own store, causing Shopify to POST a legitimately HMAC-signed webhook to the app's endpoint (attacker can capture this raw body/HMAC via any request logging they control, e.g. a proxy on their own infra since it's their own shop's traffic).
2. Attacker replays the exact same `raw_body` and `X-Shopify-Hmac-Sha256` header value to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a request object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, raw_body)` — unchanged from step 1 — and passes: [8](#0-7) .
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker's order body, despite the request never having been produced or signed with knowledge of anything shop-specific to the victim: [2](#0-1) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```

**File:** docs/usage/webhooks.md (L12-14)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```

**File:** lib/shopify_api/auth/oauth.rb (L64-76)
```ruby
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?

          state = cookies[SessionCookie::SESSION_COOKIE_NAME]
          raise Errors::NoSessionCookieError unless state

          raise Errors::InvalidOauthError,
            "Invalid state in OAuth callback." unless state == auth_query.state

          null_session = Auth::Session.new(shop: auth_query.shop)
          body = {
            client_id: Context.api_key,
            client_secret: Context.api_secret_key,
```
