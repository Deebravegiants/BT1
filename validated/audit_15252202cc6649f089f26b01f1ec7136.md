## Title
Webhook shop/topic identity spoofing via headers uncovered by HMAC signature - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body, then trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from unauthenticated HTTP headers to route and tag the payload. Because these header fields are never included in the HMAC computation, they can be freely altered by anyone able to submit a request to the app's public webhook endpoint, as long as they can attach a `(body, hmac)` pair that is valid for the app's shared `client_secret`.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` verifies authenticity with: [1](#0-0) 

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [1](#0-0) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only the raw HTTP body, while `topic`, `shop`, `api_version`, and `webhook_id` are read straight from HTTP headers with no coverage by the signature: [3](#0-2) 

The equality the code implicitly (and incorrectly) assumes is:
`shop/topic/webhook_id/api_version dispatched to the handler == shop/topic/webhook_id/api_version that Shopify actually sent for that HMAC-authenticated body`

But the real binding enforced by the code is only:
`HMAC(body, client_secret) is valid`

Since `client_secret` (`Context.api_secret_key`) is the same value for every shop that has installed the app (it is the app's OAuth client secret, not a per-tenant secret), any merchant that has the app installed can trigger a real webhook to capture a valid `(body, hmac)` pair, then submit that exact pair directly to the app's public webhook endpoint with a forged `x-shopify-shop-domain` and/or `x-shopify-topic` header. `Registry.process` will accept it as valid (the HMAC check only inspects the body) and will invoke the registered handler with `WebhookMetadata` carrying the attacker-chosen `shop` and/or `topic`, while the `body` content actually belongs to the attacker's own store.

### Impact Explanation
Any webhook handler that uses `WebhookMetadata#shop` to identify the tenant (e.g., to look up a merchant's stored session/access token, write incoming data against that shop's records, or make follow-up authenticated API calls "on behalf of" that shop) can be tricked into associating attacker-controlled webhook body data with an arbitrary victim shop domain. This breaks the tenant isolation boundary the gem is expected to guarantee for webhook processing, since the shop identity used downstream is never actually authenticated — this maps to the report's "cross-tenant access" analog (shop authenticated by HMAC vs. shop used as the tenant key are two different things).

### Likelihood Explanation
No secrets, tokens, or elevated access are required beyond installing the app on any shop (a normal, unprivileged action) in order to obtain one legitimate `(body, hmac)` pair, and the ability to send an arbitrary HTTP POST directly to the app's public webhook endpoint (webhook endpoints are, by design, publicly reachable URLs). The header fields are not cryptographically bound to the signed body anywhere in `lib/shopify_api/webhooks/**`, so this is a straightforward, repeatable attack path.

### Recommendation
- Include `topic`, `shop`, and `webhook_id` in the value that is HMAC-verified (e.g., by binding them into `to_signable_string`), or otherwise cryptographically bind the header values to the signed payload.
- At minimum, cross-check the `shop` header against the shop identifier embedded inside the JSON body (Shopify webhook payloads normally include shop-identifying fields) before dispatching to handlers, and reject on mismatch instead of trusting the header outright.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`) to capture a real request with headers `x-shopify-topic: orders/create`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid hmac>` and body `B`.
2. Attacker POSTs the exact same body `B` and the same `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against the shared secret [4](#0-3) .
4. `Registry.process` invokes the handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: <attacker's own data>)` [5](#0-4) , causing the app to process attacker-controlled data under the victim tenant's identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
