### Title
Webhook shop identity (`shop-domain` header) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body, then passes the `shop` value taken from an unauthenticated HTTP header directly to the app's handler. Because the shop identity is never bound into the signed material, any party who can obtain one valid `(body, hmac)` pair for an app (e.g., by installing the app on their own store) can replay that exact body/signature to the app's webhook endpoint while substituting an arbitrary `shop-domain` (or `x-shopify-shop-domain`) header, causing the handler to process the payload as if it originated from a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` exposes `shop` from an HTTP header that is completely independent of the HMAC: [1](#0-0) [1](#0-0) 

```
def shop
  T.cast(shopify_header("shop-domain"), String)
end
...
def to_signable_string
  @raw_body
end
```

`Utils::HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (i.e. the raw body) and compares it to the `hmac-sha256` header: [2](#0-1) 

`Registry.process` uses this single check as the sole gate before trusting `request.shop` and forwarding it to the application's webhook handler: [3](#0-2) 

Because the same app secret is shared across every shop that installs the app, and because the signature never incorporates the shop domain, `shop` is a field acted on (used as the tenant identity passed to `WebhookMetadata`/the handler) but not covered by the HMAC. This breaks the intended binding:

`hmac_valid(body, secret) == true` should imply `shop == the actual shop that sent this webhook`

but in reality it only implies `shop-domain header == whatever value the request sender chose to send`.

An unprivileged internet user can:
1. Install the target app on their own (attacker-controlled) development/trial store, which is free and requires no privileges.
2. Receive one legitimate webhook delivery from Shopify for their own store — this gives them a genuinely valid `(raw_body, hmac-sha256)` pair signed with the app's real secret.
3. Replay that exact body and HMAC directly to the app's public webhook endpoint, but with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header changed to a victim shop's domain.
4. `HmacValidator.validate` passes (body/signature unchanged), and `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"`, letting the attacker inject events/data attributed to a shop they do not control.

### Impact Explanation
This is a cross-tenant access vulnerability: the webhook processing pipeline lets an attacker impersonate any other shop that uses the app, forging arbitrary webhook events (e.g. `app/uninstalled`, `orders/create`, `customers/data_request`) under a victim tenant's identity. Downstream host applications that key session/data lookups off `WebhookMetadata#shop` (the documented pattern for this library) will act on attacker-supplied data believing it came from the victim's store, crossing the tenant boundary the library is meant to enforce.

### Likelihood Explanation
Exploitation requires no privileged credentials, no access token, and no TLS interception — only the ability to install the target app on an attacker-owned store (trivial and free) and issue a normal HTTP POST to the app's public webhook endpoint. This is realistically reachable by any unprivileged internet user who can find/guess the app's webhook route.

### Recommendation
Bind the shop identity into the authenticated material, e.g. include the `shop-domain` header (and ideally `topic`/`webhook-id`) in the HMAC-signed string, or otherwise cryptographically verify that the `shop` value matches a shop the signature was actually issued for, before it is trusted or forwarded to handlers in `ShopifyAPI::Webhooks::Registry.process`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. updates a product) to receive a legitimate delivery:
   ```
   POST /webhooks
   x-shopify-topic: products/update
   x-shopify-hmac-sha256: <valid-hmac-for-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   Body: {"id": 123, ...}
   ```
2. Attacker resends the identical body and `x-shopify-hmac-sha256` value to the same endpoint, only changing the shop header:
   ```
   POST /webhooks
   x-shopify-topic: products/update
   x-shopify-hmac-sha256: <same-valid-hmac-for-same-body>
   x-shopify-shop-domain: victim-shop.myshopify.com
   Body: {"id": 123, ...}
   ```
3. `ShopifyAPI::Utils::HmacValidator.validate` (see [4](#0-3) ) succeeds because it only checks the body/signature, unaffected by the header change.
4. `ShopifyAPI::Webhooks::Registry.process` (see [3](#0-2) ) invokes the registered handler with `shop: "victim-shop.myshopify.com"`, letting the attacker's payload be processed as if it came from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
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
