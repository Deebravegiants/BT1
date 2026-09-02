### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body. The `shop` (and `topic`/`webhook_id`) values that are handed to the app's handler as the tenant identity come from unauthenticated HTTP headers that are never included in the signed material, breaking the intended binding: `HMAC-verified bytes == bytes the app trusts as belonging to a given shop`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are read directly from HTTP headers with no cryptographic linkage to the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (i.e., the body only) and compares it with the `hmac` header value: [3](#0-2) 

`Registry.process` only checks this body HMAC and then immediately forwards the caller-supplied, HMAC-unverified `shop` header value straight to the handler as the tenant identity: [4](#0-3) 

`api_secret_key` is a single shared secret configured once for the whole app via `ShopifyAPI::Context.setup`, shared across every shop that installs the app — it is not shop-specific. Consequently any shop that has legitimately installed the app can obtain a validly-HMAC-signed webhook body of their choosing (by triggering any webhook topic on their own store), and then replay that exact `raw_body` + `hmac` header pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a different, victim shop's domain. Because the HMAC never covers the shop header, `Utils::HmacValidator.validate` still returns `true`, and `Registry.process` will invoke the topic handler with `WebhookMetadata` claiming the event happened for the victim's shop — an identity-binding break of the exact class described in the reference report ("a field acted on but not covered by the HMAC"), here manifesting as: `shop authenticated (HMAC-verified body) != shop attributed to the event (unauthenticated header)`.

Any host application that follows this gem's documented pattern (`docs/usage/webhooks.md`, lines 123–136: pass `request.headers.to_h` and `request.raw_post` straight into `Webhooks::Request`, then `Registry.process`) and uses `WebhookMetadata#shop` to select which merchant's local data to read/update is directly exposed, since the gem provides no header-to-signature binding and no cross-check against a known/expected shop.

### Impact Explanation
This allows cross-tenant confusion: an attacker who owns even one shop where the vulnerable app is installed can forge webhook deliveries that the app's own signature-verification logic accepts as authentic for an arbitrary other tenant (shop domain string is fully attacker-controlled once the HMAC check is satisfied). Depending on how the host app uses `WebhookMetadata#shop`/`#body` (e.g., updating order/customer/inventory data keyed by shop, or triggering session/webhook-driven actions scoped to "the shop in the payload"), this can lead to cross-tenant data corruption or disclosure — matching the "cross-tenant access" Critical impact bucket, since the binding broken (`shop` identity vs. verified bytes) is exactly the kind of tenant-isolation guarantee `Registry.process` is supposed to provide.

### Likelihood Explanation
Likelihood is limited by two factors: (1) the attacker must control an app installation on at least one real shop (a normal, unprivileged merchant account, not a privileged credential) to obtain a validly HMAC-signed body/hmac pair, and (2) the impact depends on the host application's handler trusting `data.shop` for tenant-scoped actions, which is the pattern this gem's own documentation encourages. No `api_secret_key`, access token, or other privileged credential is required — only ordinary use of the app as one tenant among many, satisfying the "unprivileged internet user" bar.

### Recommendation
Bind the shop identity to the signed material, e.g. by including the `x-shopify-shop-domain` (and ideally `topic`) header content in the value that is HMAC-verified (mirroring how `Auth::Oauth::AuthQuery#to_signable_string` already includes `shop` in its signed payload), or by requiring `Registry.process` callers to supply/validate an expected shop and rejecting mismatches before invoking the handler. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be trusted for tenant selection without an out-of-band check (e.g., confirming the shop has an active, previously-established session/installation record).

### Proof of Concept
1. App is installed on `attacker.myshopify.com` and `victim.myshopify.com`, both webhooks signed with the same app-wide `api_secret_key`.
2. Attacker triggers any webhook topic on their own shop, capturing the raw POST body `B` and the resulting `x-shopify-hmac-sha256` header value `H` — a valid pair since `H = HMAC_SHA256(api_secret_key, B)`.
3. Attacker sends a forged HTTP request to the app's webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com` (and any desired `x-shopify-topic`/`x-shopify-webhook-id`).
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` succeeds; `Utils::HmacValidator.validate` recomputes `HMAC_SHA256(api_secret_key, B)`, matches `H`, and returns `true`. [5](#0-4) 
5. `Registry.process` dispatches to the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, even though the payload actually originated from the attacker's own shop — the host app now processes attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
