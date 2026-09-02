## Title
Webhook `shop-domain` (and `topic`/`webhook_id`) headers are not covered by the HMAC signature, allowing cross‑tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

## Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly and unauthenticated from HTTP headers. `Registry.process` verifies only that the HMAC of the body is valid, then dispatches the handler with the unauthenticated `shop` value. This breaks the identity binding `shop attested by the HMAC == shop delivered to the app's webhook handler`, analogous to the report's core flaw where a field that drives privileged behavior (the wallet/recipient) is not bound to the value actually verified.

## Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from headers without any cryptographic binding to the signed payload: [2](#0-1) 

`HmacValidator.validate` only ever checks `verifiable_query.hmac` against `HMAC(secret, to_signable_string)`, i.e. against the body bytes, never against the head

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
