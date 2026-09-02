## Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop-domain` header — the field that identifies *which tenant* the webhook belongs to — is never part of the signed bytes. `Registry.process` validates the HMAC and then unconditionally trusts `request.shop` when building the `WebhookMetadata` passed to the app's handler. Because the app's `client_secret` (`Context.api_secret_key`) is shared across every shop that installs the app, any user who can get one webhook delivered to their own store (e.g. by installing the app on a free/dev shop they control) obtains a validly-signed `(body, hmac)` pair. They can then replay that exact body+HMAC to the app's public webhook endpoint while substituting the `shop-domain` header for a victim shop, and the signature check still passes because the header was never covered by the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from an unauthenticated header, with no involvement in the signature: [2](#0-1) 

`HmacValidator.validate` calls `verifiable_query.to_signable_string`, i.e. only the body, to compute the expected signature: [3](#0-2) 

`Registry.process` validates the HMAC and then forwards the untouched, unauthenticated `request.shop` value to the app's handler as tenant identity, with no cross-check against any authenticated value: [4](#0-3) 

The binding that should hold is:
`shop_header == shop_that_produced(body, hmac)`

but the gem only verifies `hmac == HMAC(secret, body)`, independent of `shop_header`. Since `Context.api_secret_key` is the app's single `client_secret`, shared by all shops that install the app, any of the app's own installs (including a free dev store an attacker fully controls) can produce a `(body, hmac)` pair that is valid under this same secret. An attacker can then send that pair to the app's webhook endpoint with an arbitrary `shop-domain` header value, and `Utils::HmacValidator.validate` will report success because it never looks at the header.

### Impact Explanation
This breaks the tenant-identity binding at the exact place called out by the "unprivileged user" rule set: a field (`shop`) that is acted upon (used to attribute the webhook data to a specific merchant) but not covered by the HMAC. If the host application uses `WebhookMetadata#shop` to decide which merchant's records to update/create (the documented and expected use of this field), an attacker can inject fabricated webhook events that the app attributes to a victim shop it has never actually interacted with — a cross-tenant data-integrity/confusion issue satisfying the Critical "cross-tenant access" bar in the rules.

### Likelihood Explanation
The attacker only needs to be able to install the target app on any shop they control (which is normal, unprivileged app-installation activity) and be able to send an HTTP request to the app's public webhook URL. No access token, `client_secret`, or privileged account is required — this is exactly the "unprivileged internet user" threat model in scope.

### Recommendation
Bind the shop identity to the signed content. Options:
1. Include `shop-domain` (and ideally `topic`/`webhook-id`) in the bytes that are HMAC-verified, matching how Shopify itself is expected to authenticate the payload end-to-end, or
2. Require the consuming app to cross-check `request.shop` against an installed/known shop record before trusting it, and document this requirement prominently since the gem currently gives no such warning.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com` (a store they control), triggering any subscribed webhook topic (e.g. `products/update`). They capture the raw request body `B` and the corresponding `X-Shopify-Hmac-Sha256` header value `H` that Shopify computed with the app's shared `client_secret`.
2. Attacker crafts a new HTTP POST to the app's webhook endpoint with:
   - Body: the same `B`
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (changed)
   - Header `X-Shopify-Topic`, `X-Shopify-Webhook-Id` set arbitrarily
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers, and `Utils::HmacValidator.validate` succeeds because it only recomputes `HMAC(secret, B)`, which still matches `H`.
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed_body_of_B, ...)`, causing the app to process attacker-supplied data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
