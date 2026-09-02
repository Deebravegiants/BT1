### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity is trusted from unauthenticated HTTP headers while the HMAC only covers the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authorizes a webhook purely by validating an HMAC over the raw request body, then blindly trusts the `shop`, `topic`, `webhook_id`, and `api_version` values from HTTP headers that are **not** included in the signed material, and hands them to the host app's handler as if they were verified.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

`to_signable_string` returns only `@raw_body`, so the HMAC verification performed by `HmacValidator.validate` — `OpenSSL.secure_compare(computed_signature, received_signature)` over `verifiable_query.to_signable_string` — proves only that the **body bytes** were signed with the app's secret: [2](#0-1) 

However, `shop`, `topic`, `webhook_id`, and `api_version` are read directly from the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, and `shopify-api-version` headers, none of which are part of the signed string: [3](#0-2) 

`Registry.process` then uses the *unverified* `topic` to select a handler and forwards the *unverified* `shop` (and other header values) directly into `WebhookMetadata`, which is passed to the host app's handler as authoritative: [4](#0-3) [5](#0-4) 

The binding that should hold is: `shop-header == shop-bound-in-signature`. Instead the gem verifies `hmac(body) == hmac(body)` while `shop` (and `topic`/`webhook_id`) are parsed but never bound to that signature — exactly the "bytes verified versus bytes parsed" / "shop authenticated versus shop stored" identity-binding break.

**Attack path (unprivileged internet user):** An attacker can freely sign up for a Shopify development/trial store and install the target app (this only requires normal OAuth, no special privilege). Shopify will then deliver genuinely HMAC-signed webhooks (signed with the *app's* `client_secret`, not the attacker's) to the app's webhook endpoint for the attacker's own shop. The attacker intercepts one such request (their own traffic, so they legitimately see it), and replays it to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to a victim shop's domain (and/or the `shopify-topic` header rewritten to a different topic). Because `to_signable_string` only covers `@raw_body`, the HMAC still validates successfully — the body wasn't modified — even though `shop`/`topic` were changed. `Registry.process` then invokes the handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"` even though the request never actually originated from that shop.

### Impact Explanation
This breaks the tenant-identity binding the whole webhook-authentication flow is supposed to provide: a valid signature is treated as proof that both the body *and* the shop/topic metadata came from Shopify for that specific merchant. Host applications built on this gem's documented `WebhookMetadata.shop`/`.topic` typically use these fields to look up per-shop sessions/records and act on that shop's data (e.g., apply an `orders/create` payload to the wrong merchant's account, or trigger `shop/redact` / `customers/data_request` GDPR handlers under an attacker-chosen shop). Since the "trust boundary" (HMAC check) is presented by the gem as sufficient authentication of the whole `WebhookMetadata` object including `shop`, this is a cross-tenant data confusion primitive reachable by any internet user who can install the app on a shop they control, satisfying the Critical "cross-tenant access" impact bucket.

### Likelihood Explanation
Likelihood is high: no credentials, access tokens, or the app's `client_secret` are needed — only the ability to install the target app on any Shopify store (available to anyone) and intercept/replay one's own outbound webhook HTTP request with a modified header, which is trivial with any HTTP proxy/tool. The vulnerable code path (`Request#shop`/`#topic` sourced from headers, `to_signable_string` = body-only) is exercised on every `Registry.process` call, the gem's documented HTTP webhook processing entry point.

### Recommendation
Bind the identity-relevant metadata (`shop`, `topic`, `webhook_id`, `api_version`) into the signed material verified by `HmacValidator`, e.g. include these header values (canonically ordered) in `to_signable_string`, or perform an out-of-band verification that the `shopify-shop-domain` value matches an active, previously-established session/shop for the delivery before constructing `WebhookMetadata`. At minimum, document that `shop`/`topic` from `Webhooks::Request` are not covered by the HMAC and must not be trusted for authorization decisions without additional verification.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled development store `attacker.myshopify.com`.
2. Capture a legitimately delivered webhook, e.g.:
```
POST /webhooks HTTP/1.1
shopify-topic: orders/create
shopify-hmac-sha256: <valid-base64-hmac-of-body>
shopify-shop-domain: attacker.myshopify.com
shopify-webhook-id: abc-123
shopify-api-version: 2024-01

{"id": 1, "note": "attacker-controlled body"}
```
3. Resend the same request to the app's webhook endpoint with only the shop header modified:
```
shopify-shop-domain: victim.myshopify.com
```
(body and `shopify-hmac-sha256` untouched).
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks the (unchanged) body: [6](#0-5) 
5. `ShopifyAPI::Webhooks::Registry.process` builds `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` and invokes the host handler as if Shopify had verified the request came from `victim.myshopify.com`: [4](#0-3)

### Citations

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
