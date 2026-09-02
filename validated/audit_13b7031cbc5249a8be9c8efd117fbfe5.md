## Title
Webhook HMAC signature covers only the request body, not the `shop-domain` header — allows cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `Registry.process` trusts `request.shop` (read from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` header) to identify which tenant a webhook belongs to. The HMAC verification therefore authenticates the *body*, but the *shop* field that the application actually acts on is never bound to that signature — an equality mismatch between "bytes verified" and "bytes acted on."

### Finding Description
`Registry.process` verifies webhooks like this: [1](#0-0) 

The HMAC check calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` and compares it to the `hmac` header value using the shared, app-wide `Context.api_secret_key`: [2](#0-1) 

But `Request#to_signable_string` is defined as just the raw body — it does not include `shop`, `topic`, or any other header: [3](#0-2) 

The `shop` value comes straight from an attacker-controllable HTTP header with no cryptographic binding to the signed content: [4](#0-3) 

After the HMAC check passes, `shop` is handed directly to the handler as the tenant identity for the event: [5](#0-4) 

Because `api_secret_key` is a single app-wide secret shared by every installed shop (not a per-shop key), any tenant that has legitimately received one authentic webhook (with a valid `raw_body` + `hmac` pair, generated for their own shop) can capture that exact `(raw_body, hmac)` pair and resend it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` will still return `true` because the signature only ever covered `raw_body`. `Registry.process` then dispatches the payload to the handler tagged with the victim's `shop`, so the app processes/attributes the (attacker-authored) event as coming from a different tenant.

Binding that should hold: `hmac == HMAC(secret, raw_body ‖ shop)` (or equivalent shop-scoped binding). Binding that actually holds: `hmac == HMAC(secret, raw_body)`. The `shop` field acted upon by the caller is outside the authenticated set of bytes.

### Impact Explanation
This breaks the tenant-authentication boundary the HMAC is meant to enforce: an unprivileged app user (any installed shop) can make the app process fabricated events under a different, targeted shop's identity — a cross-tenant access primitive. Depending on what the app's webhook handlers do with `WebhookMetadata#shop` (e.g., writing/deleting per-shop data, triggering side effects, disabling access, updating billing state), this can lead to cross-tenant data corruption or unauthorized actions performed against a victim merchant's account, which matches the "Critical - cross-tenant access" category.

### Likelihood Explanation
Requires only that the attacker control one legitimate installed shop of the target app (an ordinary, unprivileged capability) to obtain one authentic `(raw_body, hmac)` pair, then replay it with a forged `shop-domain` header directly against the app's public webhook endpoint. No access token, `client_secret`, or privileged account is needed — only observation of one's own legitimate webhook traffic, which is trivial for any app user.

### Recommendation
Bind the shop (and ideally topic) to the HMAC-verified payload, e.g. include `shop` in `to_signable_string`, or — following Shopify's actual model — treat `shop-domain` as informational only and re-derive/cross-check the shop from a value that is itself authenticated (or require the caller to look up and use a per-shop secret/session rather than trusting the header). At minimum, `Registry.process` should not use header-supplied `shop` as an unauthenticated tenant identifier once the raw body has been verified against only the shared secret.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and triggers a webhook event, capturing the raw POST body `B` and its `x-shopify-hmac-sha256` header value `H` (valid because `H == HMAC(secret, B)`).
2. Attacker POSTs to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim.myshopify.com`.
3. `HmacValidator.validate` recomputes `HMAC(secret, B)` (per `to_signable_string` returning only `@raw_body`) — matches `H`, so validation passes: [6](#0-5) .
4. `Registry.process` calls the handler with `shop: "victim.myshopify.com"` even though the payload/HMAC were never bound to that shop: [7](#0-6) .

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
