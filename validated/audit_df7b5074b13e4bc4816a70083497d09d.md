This confirms the vulnerability: `Registry.process` at `lib/shopify_api/webhooks/registry.rb:189-200` validates only `Utils::HmacValidator.validate(request)`, which internally calls `request.to_signable_string` — defined at `lib/shopify_api/webhooks/request.rb:35-38` as `@raw_body` only. The `topic`, `shop`, `api_version`, and `webhook_id` fields, all read from HTTP headers via `shopify_header` (`lib/shopify_api/webhooks/request.rb:20-33,67-70`), are never included in the HMAC-signed content, yet `request.shop` is trusted directly as the tenant identity passed into `WebhookMetadata.new(shop: request.shop, ...)` at `lib/shopify_api/webhooks/registry.rb:198-199`.

### Title
Webhook `shop-domain` header is trusted for tenant identity but is not covered by the HMAC signature, enabling cross-tenant webhook impersonation - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body [1](#0-0) . The `shop` identity used downstream by the host application's handler is read from the `shopify-shop-domain` / `x-shopify-shop-domain` header [2](#0-1) , but `to_signable_string` — the only bytes the HMAC actually covers — is `@raw_body` alone [3](#0-2) . The equality the code implicitly assumes, "bytes verified == shop identity acted on", does not hold: the header carrying the tenant identity is completely outside the authenticated payload.

### Finding Description
`Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and compares it to the `hmac` header value using `OpenSSL.secure_compare` [4](#0-3) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`; none of `topic`, `shop`, `api_version`, or `webhook_id` — all sourced from attacker-visible/attacker-settable HTTP headers via `shopify_header` [5](#0-4)  — feed into the signed string.

`Registry.process` uses `Utils::HmacValidator.validate(request)` as the sole authentication gate, then immediately trusts `request.shop` as the tenant identity forwarded to the handler: [6](#0-5) 

Because the api_secret_key used to compute the HMAC is shared across every shop/tenant that installs the app (it is the app's single `client_secret`, not a per-shop secret), any tenant that legitimately receives a real webhook delivery from Shopify (which any merchant who installs the app can trigger, e.g. via `orders/create`) obtains a `(raw_body, valid_hmac)` pair that is valid for that same api_secret_key regardless of which shop label is attached. An attacker who controls their own shop can:
1. Install the app and capture one legitimate webhook delivery (`raw_body` + `X-Shopify-Hmac-Sha256`) sent to the app's HTTP endpoint.
2. Resend the identical `raw_body` and `hmac` header to the same endpoint, but replace only the `X-Shopify-Shop-Domain` header with a victim shop's domain.
3. `Utils::HmacValidator.validate` still succeeds because it only checks `raw_body` against the shared secret — the header is never included in the check.
4. `Registry.process` proceeds to call `handler.handle` with `WebhookMetadata.new(..., shop: request.shop, ...)` using the attacker-supplied victim shop domain [7](#0-6) .

Any host application logic that uses `data.shop` to select tenant-scoped state (look up sessions/tokens for that shop, write per-shop records, trigger `customers/redact` or `shop/redact` compliance actions, etc., per the mandatory topics defined at `lib/shopify_api/webhooks/registry.rb:8-12`) will act on the victim shop's identity using attacker-controlled body content, a direct crossing of the tenant boundary the gem is supposed to enforce.

### Impact Explanation
This breaks the identity binding `shop_authenticated == shop_acted_on`: the HMAC only authenticates the body content, while the shop identity used for all downstream tenant-scoped actions is taken from an unauthenticated header. This is a cross-tenant access vulnerability (Critical), since it lets an attacker with access to only their own tenant (a normal, unprivileged app-install merchant) impersonate webhook traffic as coming from an arbitrary victim shop, without ever needing the app's private `api_secret_key`, the victim's access token, or any credential belonging to the victim.

### Likelihood Explanation
Likelihood is realistic for any unprivileged internet user who can install the target app on their own store (a normal, low-privilege action): they only need to capture one real webhook delivery for their own shop (trivial, since they control that shop and can trigger events like `orders/create`) and replay it with a modified `shop-domain` header to the app's public webhook endpoint. No cryptographic secret needs to be recovered because the HMAC check never examines the header at all.

### Recommendation
- **Short term**: Include the header-derived identity fields (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC verification in `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind the shop domain to the signed payload before it is trusted by `Registry.process`/`WebhookMetadata`. At minimum, document that `WebhookMetadata#shop` is not authenticated and host applications must independently verify the shop against a known-installed-shop list before use.
- **Long term**: Cross-check the header-derived `shop` against the shop associated with the currently active/expected session or an app-maintained list of installed shops before dispatching to a handler, so a validly-signed body for tenant A cannot be relabeled as belonging to tenant B.

### Proof of Concept
```ruby
# Attacker owns shop "attacker-shop.myshopify.com" and has installed the target app.
# Step 1: Attacker triggers a real webhook (e.g. orders/create) and captures the
# exact raw body + legitimate "X-Shopify-Hmac-Sha256" header Shopify sent to the
# app's webhook endpoint. This HMAC is valid because HmacValidator only signs the body:
#
#   lib/shopify_api/utils/hmac_validator.rb:26-31
#     computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
#   lib/shopify_api/webhooks/request.rb:35-38
#     def to_signable_string; @raw_body; end

captured_raw_body = '{"id":123,"note":"hello"}'
captured_hmac_b64  = "<valid hmac captured from real Shopify delivery to attacker's own shop>"

# Step 2: Attacker replays the same body/hmac to the app's public webhook endpoint,
# but swaps only the shop-domain header to the victim's shop.
post "/webhooks",
  body: captured_raw_body,
  headers: {
    "X-Shopify-Topic"        => "orders/create",
    "X-Shopify-Hmac-Sha256"  => captured_hmac_b64,
    "X-Shopify-Shop-Domain"  => "victim-shop.myshopify.com", # unauthenticated, attacker-controlled
    "X-Shopify-Webhook-Id"   => "forged-id",
    "X-Shopify-Api-Version"  => "2024-01",
  }

# Step 3: ShopifyAPI::Webhooks::Registry.process(request) passes HMAC validation
# (lib/shopify_api/webhooks/registry.rb:190) because it only checks the raw body,
# then dispatches WebhookMetadata(shop: "victim-shop.myshopify.com", ...) to the
# app's handler (lib/shopify_api/webhooks/registry.rb:198-199), impersonating the
# victim tenant.
```

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L65-70)
```ruby
      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
