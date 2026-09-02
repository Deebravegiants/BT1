### Title
Webhook HMAC only covers the raw body, not the `shop-domain` header, allowing cross-tenant webhook shop-spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (and `topic`, `api_version`, `webhook_id`) values used to route and label the webhook to the host app come from unauthenticated HTTP headers. `Registry.process` verifies the HMAC of the body and then dispatches the handler using the header-derived `shop`, so the "verified bytes" and the "acted-upon shop identity" are two different, independently-controllable things.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from caller-supplied HTTP headers with no cryptographic binding to the body/HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC of the body via `Utils::HmacValidator.validate(request)`, and once that passes, blindly trusts `request.shop` (and other headers) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (the raw body, in this case) and compares it to the `hmac` value from the (also header-derived) `hmac-sha256` header: [4](#0-3) 

The identity binding that should hold is: `shop header value == shop that produced/authorized this exact HMAC`. In reality the code only enforces `HMAC(body) == received_hmac`; it never binds `shop-domain` (or `topic`/`webhook_id`) into that signature computation. Since Shopify webhook signing uses the app's single `client_secret` (shared across every shop that has the app installed), a value that legitimately signs body B for one shop is *also* a valid signature for body B regardless of which shop header accompanies it. This is structurally the same class of bug as the ATokenERC6909 report: a field that is *acted upon* (there, `pool`/underlying address; here, `shop-domain`) is not the field that was actually *verified* (there, a static-call return value corrupted by fallback execution; here, the raw body HMAC), breaking the equality the code implicitly assumes.

### Impact Explanation
An unprivileged internet user who controls (or has previously received) one legitimate, validly-HMAC'd webhook body/signature pair for the app (e.g., by installing the app on their own store and capturing an inbound webhook, or simply computing/observing any valid body+HMAC pair since HMAC verification doesn't bind it to a specific shop) can resend that exact body and HMAC to the host app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header for a different, victim shop. `Registry.process` will pass HMAC validation (it only checks the body) and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop. Any host application that uses `WebhookMetadata#shop` to select which tenant's records to create/update/delete (a documented, intended use of this field) will write or act on data under the wrong tenant's identity — this is a cross-tenant data confusion / cross-tenant access primitive, and for mandatory compliance topics (`shop/redact`, `customers/redact`, `customers/data_request`) it could be used to trigger destructive redaction actions attributed to a shop that never sent the data.

### Likelihood Explanation
Fairly reachable: getting one genuine signed webhook body is trivial (install the app on any store you control, or already have webhook traffic from your own shop), and the header manipulation requires no secret, credential, or privileged account — just the ability to send an HTTP POST to the app's public webhook endpoint with attacker-chosen headers. No cryptographic material beyond a previously-observed valid HMAC/body pair is needed to reuse it under a different `shop-domain`.

### Recommendation
Bind the shop identity (and ideally topic/webhook-id) into the signed material, or otherwise cryptographically tie the header claims to the verified body. Concretely:
- Include `shop`, `topic`, and `webhook_id` in `to_signable_string` (Shopify's HMAC is computed over the raw body by design, so this may require deriving/validating shop identity another way, e.g., looking up the shop's own stored offline access token/session rather than trusting the header verbatim), or
- Require the host application to independently corroborate `request.shop` against a shop it has an active session/install record for before acting on the webhook payload, and document this requirement clearly since the gem itself cannot bind an unsigned header to a signed body.

### Proof of Concept
1. Install the app on `attacker.myshopify.com` and capture one legitimate webhook delivery: raw body `B`, headers including `X-Shopify-Hmac-Sha256: H`, `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: customers/redact`, `X-Shopify-Webhook-Id: W`.
2. Send a new POST to the host app's webhook endpoint with the identical body `B` and `X-Shopify-Hmac-Sha256: H`, but replace `X-Shopify-Shop-Domain` with `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds a request whose `hmac` still equals `H` and whose `to_signable_string` is still `B`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only re-derives HMAC from `B` and compares to `H`. [5](#0-4) 
5. The registered handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though `B` was never generated for that shop, and any tenant-scoped action the handler performs is misattributed to `victim.myshopify.com`.

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
