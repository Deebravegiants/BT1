### Title
Webhook `shop` and `topic` fields are trusted from unauthenticated HTTP headers, not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop`, `topic`, `api_version`, and `webhook_id` fields exclusively from HTTP headers, while `to_signable_string` (used for HMAC verification) only covers the raw request body. This breaks the identity binding: `shop` verified via HMAC == `shop` attributed to the webhook data delivered to the handler.

### Finding Description
`Webhooks::Registry.process` validates a webhook request by calling `Utils::HmacValidator.validate(request)`, which computes the HMAC over `request.to_signable_string` and compares it to `request.hmac`: [1](#0-0) 

`Request#to_signable_string` returns only `@raw_body` - it does not include the `shop`, `topic`, or any other header value: [2](#0-1) 

Meanwhile, `request.shop` and `request.topic` are read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` and `shopify-topic` / `x-shopify-topic` headers with no cryptographic binding to the signed body: [3](#0-2) [4](#0-3) 

After HMAC validation passes, `process` forwards `request.shop`, `request.topic`, and the parsed body to the app's handler: [1](#0-0) 

This is exactly the pattern flagged by the analog rule: "a field acted on but not covered by the HMAC." Contrast this with `ShopifyAPI::Auth::Oauth::AuthQuery`, where `shop` **is** included in `to_signable_string` and therefore is cryptographically bound to the HMAC: [5](#0-4) 

Because the webhook `shop` header is not part of the signed payload, an attacker who can obtain one valid `(raw_body, hmac)` pair signed with the store's `api_secret_key`-derived signature (e.g., by being the recipient of their own legitimate webhook, or via any mechanism that lets them replay a previously observed valid webhook request) can resubmit the same body/HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. `HmacValidator.validate` will still succeed, since it only checks the raw body against the HMAC, and the handler will process the payload as if it belongs to a different shop (`data.shop`, `data.topic` come straight from headers): [6](#0-5) 

### Impact Explanation
This breaks the identity binding "shop authenticated via HMAC == shop the app attributes the delivered data to." A host application that uses `WebhookMetadata#shop` to scope webhook handling to a tenant (the documented purpose of this field per this gem's `Registry.process`/handler interface) can be made to apply one shop's webhook payload/topic as if it originated from a different shop, causing cross-tenant data corruption. Since the actual `hmac-sha256` value still validates against the gem's own secret-derived signature, the gem gives the host application no signal that the `shop`/`topic` headers were forged. This qualifies as cross-tenant access/confusion under the report's Critical impact criteria, because the binding is entirely mediated by this gem's `Request`/`HmacValidator` code path, not by host application misuse.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one legitimate `(raw_body, hmac)` pair (e.g., they are themselves a merchant/shop receiving genuine Shopify webhooks, or they can observe one via a non-TLS-intercepting means such as a shared/misconfigured endpoint or logging). This is a narrower likelihood than a pure "no credential" scenario, but it requires no `api_secret_key`, access token, or privileged access - only the ability to relay their own previously-received valid webhook to the target endpoint with a swapped `shop` header value. This aligns with an "unprivileged internet user" exploiting a design gap in `to_signable_string`, not a defect requiring insider access.

### Recommendation
Include the `shop` (and ideally `topic`) values in the HMAC-verified payload for webhook requests, or otherwise cryptographically bind the header-derived `shop`/`topic` to the signed body (e.g., verify that headers match values embedded in/derivable from the signed content, or require TLS + explicit host-side revalidation and document this gap clearly). At minimum, `Webhooks::Request#to_signable_string` should be reviewed against Shopify's actual webhook HMAC scheme to confirm whether `shop`/`topic` are meant to be signed elsewhere (e.g., topic-specific webhook secrets) and, if not, the gem should not expose `request.shop`/`request.topic` as trusted values without documenting that they are unauthenticated.

### Proof of Concept
1. Attacker's own shop (`attacker-shop.myshopify.com`) receives a legitimate webhook: raw body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's `api_secret_key`), header `x-shopify-shop-domain: attacker-shop.myshopify.com`, header `x-shopify-topic: orders/create`.
2. Attacker resends the exact same `B` and `H` to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `request.to_signable_string` (`= raw_body = B`) - the check passes because `B` and `H` are unchanged. [2](#0-1) 
4. `process` builds `WebhookMetadata` using `request.shop`, which now reads `"victim-shop.myshopify.com"` from the forged header, and invokes the app's handler with this shop attribution despite the HMAC never having covered it. [1](#0-0)

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L65-70)
```ruby
      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
