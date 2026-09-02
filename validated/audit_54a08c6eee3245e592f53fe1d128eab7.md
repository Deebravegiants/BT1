## Title
Webhook `shop-domain` (and `topic`, `webhook-id`, `api-version`) headers are not covered by the webhook HMAC, allowing shop-spoofed replay — cross-tenant confusion (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) from an HTTP header that is never included in the HMAC signature computation. The signature only covers the raw request body, so an attacker who can produce (or capture) one HMAC-valid webhook body/signature pair for their own shop can resubmit the same body with a forged `shop-domain` header, and `Utils::HmacValidator.validate` will still report the request as valid.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, none of which feed into `to_signable_string`: [2](#0-1) 

`Registry.process` trusts this unauthenticated `shop` value directly, forwarding it into `WebhookMetadata` for handler consumption after only validating the body's HMAC: [3](#0-2) 

`HmacValidator.validate` computes and compares the signature purely against `to_signable_string`, so it never binds the header-derived `shop` to the signature: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by HMAC == shop acted upon by the handler`. Because the header is outside the signed payload, this equality is not enforced by the gem — `request.shop` (header, attacker-controlled transport metadata) can diverge from the actual originating shop of the signed body.

### Impact Explanation
If a host application uses `WebhookMetadata#shop` (as documented/intended by this gem) to select which merchant's tenant data/session to act on when processing the webhook body, an attacker who owns any shop that installs the app can capture one legitimately-signed webhook body from their own store and resend it with a different `shop-domain` header. The HMAC check still passes because it only re-verifies the body bytes, achieving cross-tenant confusion — data or actions attributed to a shop that never actually sent that event.

### Likelihood Explanation
Exploitation requires only an installed app on any shop the attacker controls (no `api_secret_key`, no access token, no privileged account) — the attacker needs merely to be a legitimate merchant/installer of the target app to capture one valid body+HMAC pair for reuse with a spoofed header. This is reachable by an ordinary unprivileged party with respect to other tenants.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) header values in the signed payload used for verification (e.g., verify `shop-domain` was echoed inside the JSON body via a required matching field, or otherwise cryptographically bind header-derived routing metadata to the signature) so that `Utils::HmacValidator.validate` cannot pass when the header-derived `shop` differs from the shop the signature was actually generated for.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Shopify sends a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H(secret, B)`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker replays the exact same body `B` and `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Webhooks::Request.new` parses this into `shop = "victim-shop.myshopify.com"`; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` only (unchanged) and succeeds: [5](#0-4) 
5. The handler receives `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` believing the (attacker-controlled) body content originated from the victim shop.

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
