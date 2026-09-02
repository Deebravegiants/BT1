### Title
Webhook tenant identity (`shop-domain`) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the HMAC verification to the raw request body only. The `shop` (tenant identity), `topic`, `webhook_id`, and `api_version` values are read straight from HTTP headers and are never part of the signed material, yet `Registry.process` trusts `request.shop` as the tenant identity dispatched to the app's handler.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes an HMAC over whatever `to_signable_string` returns using the app-wide `Context.api_secret_key` [1](#0-0) . For webhooks, `to_signable_string` is hard-coded to the raw body only: [2](#0-1) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are parsed directly from unauthenticated HTTP headers with no cryptographic tie to the signature: [3](#0-2) 

`Registry.process` only re-checks the HMAC against the body, then unconditionally forwards `request.shop` (and `request.topic`) to the registered handler as the trusted tenant identity: [4](#0-3) [5](#0-4) 

This breaks the equality that should hold for tenant-scoped authentication: **shop the HMAC authenticates == shop the application acts on**. Here, the HMAC authenticates only the body bytes; the shop used by the handler is an independent, unauthenticated header value.

`Context.api_secret_key` (the app's `client_secret`) is shared across every merchant that installs the same app — it is not shop-specific. Consequently, a body+HMAC pair that is valid for shop A's webhook is *also* a valid HMAC for the identical body when it is replayed with a different `shop-domain`/`shopify-shop-domain` header, because the signature never covered that header in the first place.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who operates their own store on a multi-tenant app can capture a legitimate webhook delivery for their own shop (valid raw body + valid HMAC, since Shopify signs with the app's single shared secret) and resend it to the app's webhook endpoint with the `shop-domain` header changed to a victim shop's domain. `HmacValidator.validate` still returns `true` (the body is unchanged), so `Registry.process` dispatches the webhook to the handler with `WebhookMetadata.shop` set to the victim's domain. Any host application that uses `data.shop` to look up shop-scoped state, tokens, or trigger shop-scoped side effects (order sync, GDPR redaction handlers, inventory updates, etc.) will act on/for the wrong tenant using attacker-controlled body content — a cross-tenant access/data-integrity violation, meeting the Critical bar ("cross-tenant access").

### Likelihood Explanation
Any unprivileged internet user who is a legitimate merchant of the same multi-tenant app (a very low bar — anyone can install most public apps) can obtain a real, validly-signed webhook body/HMAC pair for their own shop and simply replay it to the shared webhook endpoint with a forged `shop-domain` header. No access token, `client_secret`, or privileged access is required — only observation of one webhook delivery to their own store, which every merchant naturally receives.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, and ideally `topic`/`webhook-id`) in the signed material verified by `to_signable_string`, or otherwise cryptographically bind the shop domain to the payload before trusting it (e.g., verify the shop domain returned by the HMAC-authenticated Shopify webhook subsystem out-of-band, such as cross-checking against an installed-shop registry keyed by webhook id, rather than trusting the header verbatim). At minimum, document that `request.shop` is unauthenticated and host applications must independently validate that the shop is one they have installed for/expect, rather than treating `HmacValidator.validate` as proof of the shop's identity.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and configures a webhook handler/endpoint.
2. Shopify delivers a genuine webhook to the app: body `B`, headers include `X-Shopify-Hmac-SHA256: H` (valid HMAC of `B` under the app's shared `client_secret`) and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker replays the exact same request to the app's webhook endpoint but changes only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`, keeping body `B` and `X-Shopify-Hmac-SHA256: H` unchanged.
4. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `hmac` and `to_signable_string` (`@raw_body`) are unchanged, so `Utils::HmacValidator.validate(request)` in `Registry.process` returns `true` [6](#0-5) .
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed_body_of_B, ...)`, causing the host app to act on victim-shop data/identity using attacker-supplied content.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
