Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers and are never included in the HMAC-signed data.### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is not covered by the HMAC, allowing tenant-spoofing via header substitution on an otherwise-legitimate signed payload - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body. The `shop` (and `topic`, `webhook_id`, `api_version`) values that get passed to the app's handler are read from separate HTTP headers that are **not** part of the signed payload. This breaks the intended identity binding `authenticated_bytes == acted_upon_shop`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers, entirely outside the HMAC's coverage: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which only checks `request.to_signable_string` (the body) against `request.hmac` — it never checks the headers — and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` when building the metadata handed to the app's handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` compute and compare the signature purely against `verifiable_query.to_signable_string`, so any header value not included in that string is unauthenticated as far as this check is concerned: [4](#0-3) 

Because a merchant/developer with a legitimate installed app instance can capture a genuinely-signed webhook body+HMAC pair sent to their own shop (this is normal, unprivileged access — every app has many merchants receiving valid webhooks), that captured `(raw_body, hmac)` pair remains a valid signature for **any** value of the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, or `X-Shopify-Webhook-Id` headers, since those bytes were never part of what was signed. Replaying the same signed body while substituting a different shop's domain in the header will still pass `Utils::HmacValidator.validate(request)`, and the forged `shop` value will be handed to the app's `WebhookHandler` as if it were authenticated.

This is exactly the identity-binding failure pattern called out: "a field acted on but not covered by the HMAC." The equality that should hold — `shop_header == shop_covered_by_signature` — does not; the signature only binds the body, not the tenant identity claimed in the headers.

### Impact Explanation
This enables cross-tenant data confusion: an attacker who controls or has access to any shop with the target app installed can forge webhook deliveries that appear to originate from an arbitrary other shop (by swapping the `shop-domain` header on a validly-signed body), or can relabel the `topic`/`webhook_id` on a signed payload to trigger unintended handler logic for another topic. Any app whose `WebhookHandler` trusts `data.shop` to select tenant context (e.g., loading that shop's stored access token, writing records under that shop's ID, or triggering per-tenant side effects) can be manipulated into acting on/for the wrong tenant — a cross-tenant access condition. This matches the "cross-tenant access" Critical-impact category since the shop identity used to scope tenant data is not authenticated.

### Likelihood Explanation
High. No secret key or special privilege is needed — only the ability to receive one legitimate webhook from Shopify for any account with the app installed (something available to any developer or trial merchant who installs the app), plus the ability to POST an HTTP request to the app's public webhook endpoint with modified headers. Constructing the forged request requires no cryptographic knowledge because the body/HMAC pair is reused unmodified.

### Recommendation
Bind the `shop`, `topic`, and `webhook_id` values into the signed material, or otherwise authenticate them independently of the body-only HMAC. Concretely:
```diff
 sig { override.returns(String) }
 def to_signable_string
-  @raw_body
+  "#{shop}|#{topic}|#{webhook_id}|#{@raw_body}"
 end
```
and update the signature verification/documentation accordingly (note this changes the wire format understanding — the safer fix within the gem's control is to require and check that the header-derived `shop`/`topic` match values embedded in the (parsed) body when available, or to document/enforce that callers must independently verify `shop` against a known/allow-listed session before trusting `WebhookMetadata`). At minimum, `Registry.process` should not treat `request.shop`/`request.topic`/`request.webhook_id` as trusted merely because `Utils::HmacValidator.validate(request)` returned true, since that check never covers those fields.

### Proof of Concept
1. App has two shops installed, `attacker-shop.myshopify.com` (attacker-controlled, e.g., a free dev store) and `victim-shop.myshopify.com`.
2. Shopify delivers a legitimate webhook to the app for `attacker-shop.myshopify.com`:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-of-raw-body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   Body: {"id": 1, ...}
   ```
   The attacker captures this exact `(raw_body, hmac)` pair (e.g., via their own request logs/proxy on infrastructure they control).
3. Attacker replays the identical body and HMAC header to the app's webhook endpoint, but substitutes the shop header:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <same-valid-hmac-of-same-raw-body>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   Body: {"id": 1, ...}          # unchanged
   ```
4. `Utils::HmacValidator.validate(request)` in [5](#0-4)  recomputes the HMAC over `@raw_body` only — identical to step 2 — so validation **succeeds**.
5. `Registry.process` then calls the app's handler with `shop: "victim-shop.myshopify.com"` [6](#0-5) , even though this webhook was never generated for or by `victim-shop`, letting the attacker inject data/events under an arbitrary tenant's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
