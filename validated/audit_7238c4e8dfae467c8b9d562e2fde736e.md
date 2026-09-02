### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body. The `shop` (and `topic`/`webhook-id`) values are read straight from unauthenticated HTTP headers and are never included in the signed payload, so a request with a genuinely valid HMAC (signed body) can be paired with an arbitrary `shop-domain` header and will still pass validation.

### Finding Description
`Utils::HmacValidator.validate` computes the expected signature from `verifiable_query.to_signable_string` and compares it to the supplied `hmac`: [1](#0-0) 

For webhooks, `to_signable_string` is defined to be only the raw body: [2](#0-1) 

But `shop`, `topic`, and `webhook_id` are all parsed directly from HTTP headers, independent of the HMAC computation: [3](#0-2) 

`Registry.process` validates the HMAC and then trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` handed to the app's handler, without any additional binding check that `shop` matches the entity that produced the signed body: [4](#0-3) [5](#0-4) 

This breaks the identity binding: `hmac == HMAC(secret, body)` should imply `shop == the tenant whose event this body represents`, but because `shop` is outside the HMAC's coverage, an attacker who obtains one genuinely-signed webhook body (e.g. from their own shop, where they control an installed app and thus legitimately receive real Shopify webhooks with valid HMACs) can resend that exact body to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. `Utils::HmacValidator.validate` still succeeds (it never looks at the header), and `Registry.process` forwards `shop: request.shop` = the victim's domain to the handler along with the attacker's own body/topic content.

### Impact Explanation
Any application built on this gem that uses `request.shop` from `WebhookMetadata` to route/attribute the webhook payload to a merchant record (the overwhelmingly common pattern, e.g. to look up the tenant's session/store and apply the payload) can be made to process attacker-supplied data under a victim tenant's identity — a cross-tenant data-injection / spoofing primitive. This matches the report's abstract bug class: a field that is acted upon (`shop`) but not covered by the authentication mechanism (the HMAC), allowing the two to be desynchronized by an unprivileged internet user who merely needs one legitimately-signed body (obtainable via their own shop's real webhook deliveries) and no access to `api_secret_key`.

### Likelihood Explanation
High likelihood of reachability: the webhook endpoint is by design public/unauthenticated, `Registry.process` is the gem's documented entry point for verifying and dispatching webhooks, and nothing in the gem cross-checks the header-derived `shop`/`topic` against the signed content. An attacker only needs a merchant account of their own (to legitimately receive one valid, signed webhook delivery from Shopify) and the ability to POST to the target app's public webhook route with modified headers — no privileged credentials, access tokens, or `client_secret` needed.

### Recommendation
Bind the tenant/topic identity into the authenticated material rather than trusting bare headers post-HMAC-check:
- Include `topic`, `shop-domain`, and `webhook-id` in the string that is HMAC-verified (if compatible with Shopify's webhook signing scheme), or
- Independently corroborate `request.shop` against a value obtained from a trusted, tenant-scoped source (e.g., verify the shop is a known/installed shop for this app before dispatch), and document to consumers of `WebhookMetadata` that `shop` must not be trusted purely because HMAC validation passed unless such corroboration exists.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook delivery, e.g.:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid HMAC of body B, computed by Shopify with the real api_secret_key>
   X-Shopify-Shop-Domain: attacker.myshopify.com
   Body: B
   ```
2. Attacker replays the exact same body `B` and `X-Shopify-Hmac-Sha256` value to the same endpoint, but changes only the shop header:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <same valid HMAC as above>
   X-Shopify-Shop-Domain: victim.myshopify.com
   Body: B
   ```
3. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only [2](#0-1)  — it matches, since `B` is unchanged.
4. `Registry.process` proceeds and calls the app's handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: <attacker's own order data>, ...)` [6](#0-5) , causing the host application to process attacker-controlled data as if it belonged to `victim.myshopify.com`.

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
