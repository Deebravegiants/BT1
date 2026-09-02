### Title
Webhook Shop-Domain Header Not Covered by HMAC Signature Enables Cross-Tenant Webhook Forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop` (tenant identity) is taken from an unsigned HTTP header. `HmacValidator.validate` therefore only proves that the *body bytes* were signed by Shopify — it proves nothing about which shop the webhook is for. An attacker who can obtain any one genuinely-signed webhook body+HMAC pair (e.g., from their own installed/trial shop) can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` / `x-shopify-shop-domain` header, and the request will still pass HMAC validation and be dispatched to the handler under the attacker-chosen shop identity.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`: [1](#0-0) 

`hmac` is derived from the `hmac-sha256` header and `shop` is derived from the `shop-domain` header — but `to_signable_string` returns only the raw body: [2](#0-1) 

`Utils::HmacValidator.validate` signs/verifies exactly `to_signable_string`, i.e., the raw body, with `Context.api_secret_key`: [3](#0-2) 

`Webhooks::Registry.process` validates the request via this HMAC check and then trusts `request.shop` (the unsigned header) as the tenant identity passed to the app's handler: [4](#0-3) 

The equality the gem implicitly claims to guarantee is: *the shop that receives the HMAC-verified body == the shop asserted by the `shop-domain` header*. In reality, the HMAC only binds the body bytes to Shopify's secret; the `shop` header is fully attacker-controlled bytes that ride along unauthenticated. This is exactly the "field acted on but not covered by the HMAC" identity-binding break called out as in-scope: `shop` is acted on (used to attribute/route the webhook to a tenant) but not covered by the signature that is verified.

### Impact Explanation
Because `shop` is not part of the signed material, any actor capable of harvesting one legitimately-signed webhook body/HMAC pair (trivially available to anyone who installs the app on their own store and receives real Shopify webhooks) can replay that same body+HMAC combination to the app's public webhook endpoint with a forged `shop-domain` header naming a different, victim shop. `Registry.process` will accept it (HMAC check only validates body integrity) and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop. Any host application that uses `request.shop`/`WebhookMetadata#shop` to scope database writes, cache invalidation, billing events, or other tenant-specific side effects will process attacker-supplied data under another merchant's identity — a cross-tenant integrity/confidentiality violation.

### Likelihood Explanation
The webhook endpoint is, by design, an unauthenticated internet-facing endpoint (that's the entire reason HMAC verification exists here). Obtaining one valid signed body/HMAC pair requires nothing more than owning/installing the app on any shop (including a free-trial/attacker-created shop) and triggering an event that produces a webhook. No access to `api_secret_key`, tokens, or victim credentials is required — only the ability to replay an HTTP POST with a different header value, which is trivial for any unprivileged actor with network access to the app's webhook route.

### Recommendation
Include the tenant-identifying header (`shop-domain`) in the material that is HMAC-verified, or independently cross-check the `shop-domain` header against a value derived from data that is itself covered by the signature (e.g., require the host application to correlate the header with the shop associated with the specific webhook subscription/topic via Shopify's API instead of trusting the header verbatim). At minimum, document prominently that `Request#shop` is unauthenticated and must not be trusted for tenant scoping without additional verification.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook-producing event to receive a real request with body `B` and header `shopify-hmac-sha256: H` (a valid HMAC of `B` under the app's shared secret).
2. Replay to the app's webhook endpoint:
```
POST /webhooks HTTP/1.1
shopify-topic: orders/create
shopify-hmac-sha256: H
shopify-shop-domain: victim-shop.myshopify.com

B
```
3. `Utils::HmacValidator.validate` recomputes HMAC over `B` only [2](#0-1)  and it matches `H`, so validation succeeds.
4. `Registry.process` dispatches the handler with `shop: "victim-shop.myshopify.com"` [5](#0-4) , even though the body actually originated from `attacker.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
