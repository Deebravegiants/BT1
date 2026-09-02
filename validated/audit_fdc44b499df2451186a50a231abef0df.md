### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the `shop` (tenant) identity used to dispatch the webhook to app handlers is read from an unauthenticated header. Since the HMAC secret (`api_secret_key`) is a single per-app secret shared across every installed shop, any entity that can obtain one validly-signed webhook body (e.g. from their own store, which every merchant legitimately receives) can replay that exact body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. `Utils::HmacValidator.validate` will still accept the request because the signature check never inspects the shop header, and the app's registered handler will be invoked believing the data belongs to the victim tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is parsed straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely independent of the signed content: [2](#0-1) 

`Registry.process` validates only the HMAC over the body via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop` to build the metadata that is handed to the app's webhook handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` recomputes an HMAC over `verifiable_query.to_signable_string` (the raw body) with `Context.api_secret_key` and compares it to the received signature — it never binds the shop field into the signed string: [4](#0-3) 

The broken identity binding is: `shop header used to attribute/dispatch the webhook` ≠ `shop bound inside the HMAC-signed bytes`. Because `api_secret_key` is one static secret per app (not per-shop), a signature valid for shop A's payload is indistinguishable, cryptographically, from a signature that would be valid for the same bytes claimed to belong to shop B — the gem provides no mechanism to detect the mismatch since the shop is simply never part of what's signed.

This is the same "field acted on but not covered by the HMAC" class of bug named in scope, applied to the webhook processing pipeline rather than the gauge-removal analog in the report (which was about an identity/permission binding — active vs. deprecated gauge — never being propagated to a dependent system that continues to act on stale identity).

### Impact Explanation
An attacker who operates or has access to any shop that has the vulnerable app installed (or who intercepts/replays one legitimate webhook delivery) can craft an HTTP POST to the app's webhook endpoint with:
- The exact raw body bytes from a real, validly-signed webhook they received for their own shop (e.g. `customers/data_request`, `orders/create`, etc., whichever topic is registered),
- The original valid `X-Shopify-Hmac-Sha256` value (unchanged, since the body is unchanged),
- A forged `X-Shopify-Shop-Domain` header set to a victim shop's domain.

`Registry.process` will accept this as authentic (HMAC still matches the body) and invoke the registered handler with `shop: <victim-shop>` and the attacker-controlled body content. Any host application that uses `shop` from `WebhookMetadata` to look up per-tenant state, trigger tenant-scoped side effects, or gate data by tenant (a documented, expected usage pattern of this field) will process attacker-supplied data as though it originated from the victim shop — a cross-tenant data-confusion/cross-tenant access primitive, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is meaningful but bounded by needing at least one legitimately-signed webhook body, which any unprivileged merchant using the app can obtain by simply installing the app on their own shop and receiving normal webhook deliveries — no access to `api_secret_key`, tokens, or privileged accounts is required. The header manipulation itself only requires the ability to send an arbitrary HTTP request to the app's public webhook endpoint.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the HMAC-signed material verified by `Webhooks::Request`, or otherwise cryptographically bind the claimed shop to the signed payload before dispatching to handlers — e.g., have `to_signable_string` incorporate the shop header, or independently verify that the shop asserted in headers corresponds to an app installation whose install-time HMAC/session artifacts match, rather than trusting the header outright once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the vulnerable app on their own shop `attacker.myshopify.com` and registers/receives a legitimate webhook delivery for topic `orders/create`, capturing the raw body `B` and the valid header `X-Shopify-Hmac-Sha256: H` (computed by Shopify over `B` using the app's single `api_secret_key`).
2. Attacker sends a new POST to the app's webhook endpoint with body `B` unchanged, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and finds it matches `H` — validation passes.
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker-controlled data attributed to the victim tenant.

### Citations

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
