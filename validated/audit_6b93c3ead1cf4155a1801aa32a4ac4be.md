This confirms enough to write the finding. The `Registry.process` method in `lib/shopify_api/webhooks/registry.rb` validates only `Utils::HmacValidator.validate(request)` (line 190), and the `Request#hmac` and `Request#to_signable_string` in `lib/shopify_api/webhooks/request.rb` bind the HMAC to `@raw_body` only, while `Request#shop` is read directly from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header. `shop` is then passed straight through to `WebhookMetadata.new(... shop: request.shop ...)` at line 198, which host apps use (per `docs/usage/webhooks.md`) as the trusted tenant identifier.

### Title
Webhook `shop` field is not covered by the HMAC, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, never the `shop-domain` header. `Registry.process` treats a valid HMAC as proof the *entire* request (including `shop`) is authentic and forwards `request.shop` unmodified to the app's webhook handler.

### Finding Description
`Request#hmac` decodes the `X-Shopify-Hmac-Sha256` header [1](#0-0)  and `to_signable_string` returns only `@raw_body` [2](#0-1) . The `shop` accessor, however, is read straight from the `shop-domain` header with no cryptographic binding to that value [3](#0-2) .

`Registry.process` accepts the request purely on `Utils::HmacValidator.validate(request)`, which internally calls `validate_signature`, comparing `computed_signature = compute_signature(verifiable_query.to_signable_string, secret)` (i.e., only the body) against the received HMAC [4](#0-3) . After this single check, `request.shop` is forwarded unauthenticated into `WebhookMetadata` and handed to the app's handler [5](#0-4) .

Shopify signs webhooks using the app's `client_secret`, which is identical for every shop that installs the app. Because `shop` is excluded from the signed bytes, the identity binding the docs imply — "`shop`, the shop domain of the webhook" is verified — does not hold: `hmac-verified(raw_body)` ≠ `hmac-verified(raw_body, shop)`. The `docs/usage/webhooks.md` "Process a Webhook" section explicitly states `Registry.process` "will verify the request did indeed come from Shopify" and then documents `data.shop` as a trustworthy field, which is misleading given the header is never bound into the signature.

### Impact Explanation
Any unprivileged internet user who can install the target app on their own (e.g., free development) store obtains genuinely Shopify-signed webhook requests whose bodies they fully control (by editing their own orders/products/customers). Because the signature never covers the `shop-domain` header, the attacker can replay that same signed body to the app's webhook endpoint while substituting an arbitrary victim shop domain in the header. `HmacValidator.validate` still returns `true`, and the handler receives `WebhookMetadata` claiming the attacker-controlled body originated from the victim shop — a cross-tenant data-injection primitive into whatever the host app does with `data.shop`/`data.body` (e.g., updating orders, customers, or triggering privileged workflows keyed by shop). This is a cross-tenant access impact.

### Likelihood Explanation
Requires only that the attacker can install the app on their own shop (typically self-serve/public) and know or guess a target shop's `.myshopify.com` domain (often discoverable). No access token, `api_secret_key`, or privileged account is required — only observing one legitimate webhook delivered to their own store.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`) in the signable string/verification, or otherwise cryptographically bind the claimed shop domain to the signed payload before trusting `request.shop` in `Registry.process`. At minimum, update the documentation to clarify that `HmacValidator`/`Registry.process` only proves body integrity/authenticity, not the authenticity of the `shop` header, so host applications do not treat `data.shop` as verified.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook (e.g., `orders/create`) with fully attacker-controlled body content, receiving a request with a valid `X-Shopify-Hmac-Sha256` signed using the app's shared `client_secret`.
3. Attacker replays the exact `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` (only checking `raw_body`) returns `true` [6](#0-5) .
5. `Registry.process` invokes the app's handler with `WebhookMetadata` carrying `shop: "victim.myshopify.com"` and the attacker's crafted body [5](#0-4) , causing the host application to process forged data under the victim tenant's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
