### Title
Webhook `shop-domain` header is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` fields used by `ShopifyAPI::Webhooks::Registry.process` to dispatch and attribute the webhook are read directly from HTTP headers that are never covered by the HMAC check. This breaks the identity binding `hmac_signed(bytes) == bytes_acted_on`, allowing a request whose body+HMAC pair is valid for one shop to be replayed with a different `shop-domain` header and be processed by the app as if it came from a different tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from request headers with no cryptographic tie to the HMAC: [2](#0-1) 

`Registry.process` validates only the body-derived HMAC, then trusts `request.topic` and `request.shop` (both unauthenticated headers) to look up the handler and construct the metadata passed to application code: [3](#0-2) 

The identity binding that should hold is: `shop identified by HMAC == shop acted on by the handler`. Because the HMAC only signs `@raw_body`, and `shop`/`topic`/`webhook_id` are excluded from that signed string, the equality does not hold — any request whose body byte sequence matches a previously-observed, HMAC-valid webhook (e.g., one the attacker legitimately received for their own low-privilege shop) can be resubmitted to the app's webhook endpoint with the `shop-domain` (and/or `topic`/`webhook-id`) header swapped to a victim shop, and it will still pass `Utils::HmacValidator.validate(request)` while being attributed and processed as belonging to the victim tenant.

### Impact Explanation
This is a cross-tenant identity-binding bypass: an attacker who legitimately installs the app on their own (low-privilege) shop can capture a valid `(raw_body, hmac)` pair from a genuine Shopify-delivered webhook to their shop, then replay that exact body/HMAC combination against the app's public webhook endpoint with a forged `shop-domain` header pointing at a victim shop. Because `Registry.process` derives the acted-upon tenant (`shop`) solely from the unauthenticated header rather than from anything covered by the signature, the application's webhook handler executes as if the event originated from the victim shop — for example, an `app/uninstalled` handler could delete or invalidate the victim's stored session/access token, or other handlers could write attacker-controlled but victim-attributed data, causing cross-tenant impact.

### Likelihood Explanation
The attacker needs no secrets and no privileged access — only the ability to install the app on a shop they control (a normal, unprivileged action) and to send an HTTP POST to the app's public webhook endpoint. The main constraint is finding/crafting a webhook body whose content is acceptable for replay under a different topic/shop (many webhook topics such as `app/uninstalled` have minimal or predictable bodies), which is a realistic scenario for at least some topics.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used for HMAC verification, or otherwise cryptographically bind the tenant identity to the signed payload before `Registry.process` uses `request.shop`/`request.topic` to dispatch to handlers. At minimum, document that consuming applications must independently verify the shop in the webhook payload matches a shop that actually has this app installed (via stored session lookup) before trusting header-derived shop attribution.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; receive a genuine webhook, e.g. `app/uninstalled`, with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac for body B>`, and body `B` (often `{}` or minimal JSON).
2. Replay a POST to the app's webhook endpoint with the identical body `B` and identical `X-Shopify-Hmac-Sha256` header, but set `X-Shopify-Shop-Domain: victim.myshopify.com` (and matching `X-Shopify-Topic` if needed).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because the HMAC only signs body `B` (`Request#to_signable_string` returns `@raw_body`), and then dispatches the handler with `shop: request.shop` set to `victim.myshopify.com`, causing the app to execute the handler logic against the victim tenant.

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
