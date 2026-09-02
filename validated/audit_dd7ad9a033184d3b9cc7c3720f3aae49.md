## Title
Webhook shop-domain and topic headers are not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read straight from unauthenticated HTTP headers. `Utils::HmacValidator.validate` only proves that the *body* was signed with the app's secret; it says nothing about which shop or topic that body belongs to. This breaks the identity binding: `shop` authenticated (nothing) ≠ `shop` acted on by the webhook handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are derived purely from HTTP headers, none of which participate in the signed content: [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes the signature over `verifiable_query.to_signable_string` (i.e. the raw body only) and constant-time-compares it to the `hmac-sha256`/`x-shopify-hmac-sha256` header: [3](#0-2) 

`Registry.process` validates only that HMAC, then dispatches the handler using the unauthenticated `shop`, `topic`, and `webhook_id` header values: [4](#0-3) 

Because the headers are not part of the signed payload, any body+HMAC pair that is valid for one shop/topic combination is also valid (per the gem's validator) for a different, attacker-chosen `shop-domain`/`topic`/`webhook_id` header combination, as long as the body bytes are unchanged. An attacker who can obtain one genuine signed webhook delivery from the app (e.g. by installing the app, even a free/public one, on a shop they control, or replaying/capturing any webhook to which they have access) can resend the exact same raw body and HMAC header to the app's public webhook endpoint while substituting the `shop-domain` header for a victim shop, and/or the `topic`/`webhook-id` headers for a different registered topic. `Utils::HmacValidator.validate` still returns `true` because it only checks the body against the secret; it never binds the signature to the header values that the handler subsequently trusts as `WebhookMetadata#shop` / `#topic` / `#webhook_id`.

### Impact Explanation
This is a Critical-severity cross-tenant issue: the gem hands the application a `shop` value that has not been authenticated in any way, letting an attacker who can produce one valid signed webhook (from their own installed shop) forge deliveries that appear to originate from an arbitrary victim shop and/or arbitrary topic. Any host application that trusts `WebhookMetadata#shop` (e.g. to look up a session, process a `shop/redact` / `app/uninstalled` mandatory webhook, or write per-tenant data) can be tricked into acting on behalf of the wrong tenant, i.e. cross-tenant access to another merchant's webhook processing path.

### Likelihood Explanation
The attacker only needs to be an unprivileged internet user who can install the target's app on a shop they control (trivial for public apps, and always possible for the mandatory `app/uninstalled`/`shop/redact` topics which every OAuth install receives) and can send arbitrary HTTP requests to the app's public webhook endpoint. No access token, `client_secret`, or leaked credential is required — only observation of one legitimately-delivered webhook body+HMAC pair for their own shop.

### Recommendation
Include the shop domain, topic, webhook id, and api version in the HMAC-signed content (or otherwise cryptographically bind them to the payload) in `Request#to_signable_string`/`HmacValidator`, so that `Utils::HmacValidator.validate` fails if any of these header values are altered relative to what Shopify actually signed.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com` (attacker-controlled) and receive a legitimate webhook delivery, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-of-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   x-shopify-webhook-id: aaaa-...
   Body: {"id": 1}
   ```
2. Replay the identical body and `x-shopify-hmac-sha256` value, but change the header:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only — unchanged — so validation succeeds: [5](#0-4) 
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though Shopify never signed anything for that shop, allowing the attacker-controlled request to be processed as if it belonged to the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
