The strongest analog to the `DropBox::tokenURI` issue is in the webhook HMAC verification path: the HMAC only binds the **request body**, while the `shop` (tenant identifier) and `topic` fields — which the app trusts and acts on — are taken from unsigned HTTP headers.

### Title
Webhook `shop` and `topic` identifiers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `Request#shop` and `Request#topic` are read straight from HTTP headers that are never included in the signed payload. `Utils::HmacValidator.validate` only checks that the HMAC matches the body, so an attacker who possesses *any* valid `(body, hmac)` pair for the app's secret (e.g., from a webhook Shopify legitimately sent them for their own store) can resend that exact body/HMAC to the app's public webhook endpoint while forging the `shop-domain` and/or `topic` headers to arbitrary values. The signature check still passes because those headers are outside what is verified.

### Finding Description
`Request#to_signable_string` only returns `@raw_body`: [1](#0-0) 

`shop` and `topic` are pulled from headers that are excluded from that signable string: [2](#0-1) 

`HmacValidator.validate`/`validate_signature` computes the signature strictly over `verifiable_query.to_signable_string`, i.e. the body only, and compares it against the received `hmac`: [3](#0-2) 

`Registry.process` trusts `request.shop` and `request.topic` directly after the HMAC check passes, and hands them to the registered handler as the tenant/topic identity for the webhook: [4](#0-3) 

The broken identity binding, expressed as an equality that should hold but doesn't:
`hmac_verified_bytes == bytes_the_app_acts_on` fails, because `hmac_verified_bytes = raw_body` while `bytes_the_app_acts_on` includes `shop-domain` / `topic` headers that are never hashed.

### Impact Explanation
This is a cross-tenant integrity break: an app installed on multiple shops (or any actor able to obtain one valid signed webhook payload+HMAC for the secret, e.g. from their own legitimate shop's webhook deliveries) can craft a request with a forged `shop-domain` header pointing at a victim shop while reusing a body+HMAC pair that remains cryptographically valid. Because `Registry.process` passes `request.shop` straight into `WebhookMetadata` without any additional binding, the host application's webhook handler will process/act on data under the wrong shop's identity — a cross-tenant access/confusion scenario, matching the Critical "cross-tenant access" impact bucket.

### Likelihood Explanation
Requires the attacker to have obtained at least one authentic `(body, hmac)` pair signed with the app's secret — for example, by being a legitimate merchant who installed the same app and thus legitimately receives real webhooks for their own store. No access to `api_secret_key` or an access token is required; only reuse of a previously-observed, validly-signed webhook body against the app's public webhook endpoint with tampered headers. This is a realistic unprivileged-actor scenario for any multi-tenant app built on this gem.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-verified payload, or otherwise cryptographically bind them to the body before verification — e.g., verify HMAC over a canonical string that concatenates the header values with the body, not just the raw body alone. At minimum, document/require host applications to independently authenticate the shop domain of incoming webhooks against known installed shops rather than trusting `request.shop` implicitly once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target app on Shop A (or otherwise legitimately receives a webhook from Shopify for Shop A) and captures the delivered `raw_body` and its `x-shopify-hmac-sha256` value — a valid signature because it was computed by Shopify using the app's real secret over that body.
2. Attacker sends a forged HTTP request directly to the app's webhook endpoint with:
   - The same `raw_body` and `x-shopify-hmac-sha256` captured above (still valid, since HMAC only covers body).
   - `x-shopify-shop-domain: shop-b.myshopify.com` (a victim tenant, instead of Shop A).
   - Optionally a different `x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the body's HMAC: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "shop-b.myshopify.com"` even though the payload actually originated from Shop A's webhook, causing the host application to process/store data under the wrong tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
