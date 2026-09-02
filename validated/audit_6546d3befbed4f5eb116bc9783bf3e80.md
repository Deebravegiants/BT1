### Title
Webhook shop identity not bound by HMAC allows cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while the `shop` (and `topic`) values used by the host application to attribute the webhook to a tenant are read directly from unauthenticated headers. This breaks the identity binding `shop_verified == shop_acted_on`: any request whose body carries a valid HMAC for the secret can be replayed with an arbitrary `X-Shopify-Shop-Domain` header and will be processed as belonging to that shop.

### Finding Description
`Registry.process` validates only the HMAC over the raw body, then forwards the shop straight from the header to the handler: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors all read from HTTP headers that are never part of the signed material: [2](#0-1) 

`HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string`, i.e., the raw body for webhooks: [3](#0-2) 

This is exactly the "field acted on but not covered by the HMAC" identity-binding break called out in the report's rule set. Contrast this with the OAuth callback flow, where `AuthQuery#to_signable_string` explicitly includes `shop` in the signed parameters, so the shop cannot be swapped without invalidating the HMAC: [4](#0-3) 

No such binding exists for the webhook `shop-domain` header. Docs confirm host apps are meant to trust `data.shop` as the tenant identifier taken straight from this unauthenticated header: [5](#0-4) 

### Impact Explanation
An unprivileged actor who can obtain even one authentic webhook delivery to their own (attacker-controlled) shop installation — a completely ordinary, non-privileged action — receives a body + valid `X-Shopify-Hmac-Sha256` pair signed with the app's real `client_secret` by Shopify. Because the HMAC never covers `shop-domain` or `topic`, the attacker can replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary victim `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`). `Registry.process` will pass HMAC validation and hand the handler `WebhookMetadata` claiming the data belongs to the victim shop, causing the host application to process attacker-supplied/attacker-shop data under another tenant's identity — a cross-tenant data-confusion vector, matching the "Critical – cross-tenant access" impact category.

### Likelihood Explanation
Medium-to-High: the prerequisite (owning/installing the app on any shop to receive one genuine webhook and capture its raw body + HMAC header) is trivial and requires no credentials, TLS interception, or privileged account — it is exactly what any developer/merchant testing the app can do. The replay itself only requires sending an HTTP POST with modified headers to the app's already-public webhook callback URL.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-covered signable string for webhooks, or otherwise cryptographically bind them (e.g., verify the shop domain returned by the webhook against a value retrieved via a signed/trusted channel, not a plain header) before constructing `WebhookMetadata`. At minimum, document prominently that `data.shop` from `ShopifyAPI::Webhooks::Request` is not authenticated by the HMAC and must be independently verified against known installed shops before use.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) to capture a legitimate `raw_body` and its `X-Shopify-Hmac-Sha256` header value, both signed with the app's real secret by Shopify.
2. Replay to the app's webhook endpoint:
   ```
   POST /callback/orders/create
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <captured hmac>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   X-Shopify-Webhook-Id: <any>
   Body: <captured raw_body>
   ```
3. `ShopifyAPI::Utils::HmacValidator.validate` succeeds (body+secret match), and `Registry.process` invokes the handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)`, causing the host app to associate attacker-controlled webhook content with the victim shop. [1](#0-0)

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```

**File:** docs/usage/webhooks.md (L10-18)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```
