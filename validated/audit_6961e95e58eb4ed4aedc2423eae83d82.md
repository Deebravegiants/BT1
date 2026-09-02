### Title
Webhook shop identity is not covered by HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/registry.rb, lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC over the raw request body, but the shop identity attached to the resulting `WebhookMetadata` handed to the app's handler is read from an unauthenticated HTTP header. The HMAC does not bind the `shop` value, so the bytes verified (`raw_body`) are not the bytes that determine which tenant the event is attributed to.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#hmac` is derived purely from the `hmac-sha256` header [2](#0-1) . The `shop` accessor, however, is read straight from the `shop-domain` header with no cryptographic binding to the signature at all [3](#0-2) .

`Registry.process` validates the webhook using `Utils::HmacValidator.validate(request)` [4](#0-3) , and `HmacValidator.validate_signature` computes the signature strictly over `verifiable_query.to_signable_string` (the raw body) [5](#0-4) . After this check passes, `Registry.process` builds `WebhookMetadata` using `request.shop` — the unauthenticated header value — and dispatches it to the app's handler as the tenant identity for the event [6](#0-5) . `WebhookMetadata.shop` is a plain `String` field with no further validation [7](#0-6) .

The equality that should hold is: *bytes verified by HMAC == bytes that determine the shop the event is attributed to*. In this code the equality breaks down: `HMAC(raw_body)` is verified, but `shop` (a separate, unsigned header) is what host applications use to attribute the event to a tenant. Since the same app-wide `client_secret` is used to sign every merchant's webhook body, and the signature never incorporates the shop domain, a valid `(raw_body, hmac)` pair captured from one legitimate webhook delivery (e.g., one sent to a shop the attacker themselves controls/installed the app on) remains valid when replayed with an arbitrary `X-Shopify-Shop-Domain` header value substituted for a victim shop. HmacValidator has no way to detect this because it never inspects the `shop` field.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook handlers: a host application receiving `WebhookMetadata` reasonably treats `shop` as an authenticated attribute of the (HMAC-verified) request, since HMAC validation is the entire authentication mechanism this gem offers for webhooks. An attacker who is a legitimate merchant of the app (or who otherwise obtains one valid `(body, hmac)` pair sent to the app, e.g. by installing the app on their own store) can replay that exact body/signature pair to the app's webhook endpoint while spoofing the `shop-domain` header to any other installed shop. `Registry.process` will accept it as valid (HMAC checks out) and hand the handler a `WebhookMetadata` claiming it is for the victim shop, with attacker-chosen body content (limited to whatever body they could get legitimately signed, but topic/mutation semantics can often be reused, e.g. `app/uninstalled`, `customers/redact`, `shop/update`-style payloads that don't depend on shop-specific IDs). This is a cross-tenant confusion vulnerability reachable by any unprivileged internet user who can install the app on their own shop or otherwise capture one signed webhook payload — no `api_secret_key`, access token, or privileged access is required.

### Likelihood Explanation
Moderate-to-high. Any developer using their own Shopify Partner account can install a target app on a store they control and receive real, validly signed webhook deliveries for arbitrary registered topics. Because those webhooks are signed only over the JSON body (which is often static or attacker-influenced, e.g. empty `{}` bodies for topics like `customers/redact`, `shop/redact`, or many others), the attacker can trivially replay the exact bytes with a forged shop-domain header pointed at any other shop known to have installed the app. The exploit requires only standard HTTP tooling and no secrets beyond what any app installer can already obtain.

### Recommendation
Bind the shop identity into the value that is cryptographically verified before it is trusted:
- Include the `shop-domain` (and ideally `topic`, `webhook-id`) header values in the signable string used for HMAC verification, or
- Require host applications to independently confirm `request.shop` corresponds to a store known to have an active session/installation associated with the specific webhook subscription (e.g., webhook_id lookup), rather than trusting the header value directly, and document this as a required check in `Registry.process`.

### Proof of Concept
1. Install the target app on an attacker-controlled development store (`attacker-shop.myshopify.com`) and trigger a webhook for a topic with a static/known body, e.g. `customers/redact` with body `{}`.
2. Capture the legitimate request Shopify sends to the app's webhook endpoint, including headers `X-Shopify-Hmac-Sha256: <valid-hmac>`, `X-Shopify-Topic: customers/redact`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, and raw body `{}`.
3. Replay this exact request to the same webhook endpoint, but replace `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
4. Because `Utils::HmacValidator.validate` (called in `Registry.process`) only checks `HMAC(raw_body)`, and never verifies the shop header, the request passes validation:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request) # passes
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)) # shop == "victim-shop.myshopify.com"
```
5. The app's `WebhookHandler#handle` implementation now processes an event as if it originated from `victim-shop.myshopify.com`, even though it was forged by the operator of `attacker-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/webhooks/registry.rb (L189-190)
```ruby
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
