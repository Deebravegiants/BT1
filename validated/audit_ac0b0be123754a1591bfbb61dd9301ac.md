### Title
Webhook `shop-domain` (and `topic`/`webhook_id`/`api_version`) headers are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body (`to_signable_string` returns `@raw_body`), while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers that are never included in the signed payload. `ShopifyAPI::Webhooks::Registry.process` validates only the body's HMAC and then trusts the header-derived `shop` value when constructing `WebhookMetadata`, which is handed to the app's webhook handler as the tenant identifier.

### Finding Description
The binding that should hold is: `HMAC-verified(bytes) == tenant-identity(bytes)`, i.e. the shop that the HMAC proves the bytes came from (Shopify, using the app's shared secret) should be the same shop the application acts on. Here that equality is broken.

- `Request#to_signable_string` only returns `@raw_body`: [1](#0-0) 
- `Request#shop`, `#topic`, `#webhook_id`, `#api_version` are pulled straight from headers, none of which are part of the signed string: [2](#0-1) 
- `Registry.process` validates only the HMAC over the body, then immediately trusts `request.shop`/`request.topic`/etc. to build `WebhookMetadata` passed to the handler: [3](#0-2) 
- The HMAC secret (`Context.api_secret_key`) is a single per-app secret, shared across every shop that installs the app, not a per-shop secret: [4](#0-3) 
- Documentation confirms `data.shop` (from the header) is the identifier apps are expected to use to route/attribute webhook data to a tenant: [5](#0-4) 

Because the HMAC only proves "these bytes were produced by someone who knows the app's `api_secret_key`" and does not bind that proof to any particular shop, any entity that has legitimately installed the app on their own store (an ordinary unprivileged merchant/attacker) can:
1. Receive a real webhook from Shopify for their own store, which comes with a valid `X-Shopify-Hmac-Sha256` for that exact raw body.
2. Replay that exact raw body + HMAC to the app's public webhook endpoint, but substitute the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header with a victim shop's domain.
3. `HmacValidator.validate` still succeeds because it only checks the body against the shared secret; the forged `shop` header is not part of the signed material and passes through to the handler as `data.shop`.

The app's webhook handler receives `WebhookMetadata` claiming the event/body belongs to the victim shop when it actually originated from, and contains data controlled by, the attacker's own shop.

### Impact Explanation
This breaks the shop/tenant identity binding on a security-relevant field. Applications are documented to key their downstream logic (job attribution, DB writes, cache invalidation, order/product records, mandatory-webhook compliance data like `customers/redact`) off `data.shop`. An attacker can inject attacker-controlled webhook bodies that the app attributes to a victim shop, which is a cross-tenant data-integrity/cross-tenant access issue: the application will act on another tenant's identity using content the attacker fully controls (subject to the topic's payload shape). This matches the "cross-tenant access" Critical impact category, since the confused identity crosses a tenant/shop boundary that the app relies on this gem to enforce.

### Likelihood Explanation
Likelihood is realistic for any unprivileged internet user: the only prerequisite is owning/controlling one shop that has the app installed (trivial - development stores are free and self-service), enabling capture of one valid `(raw_body, hmac)` pair per topic of interest. No access to the app's `client_secret`, no privileged account, and no interception of others' traffic is required - only a direct POST to the app's public webhook route with a substituted header. The webhook endpoint is by design internet-reachable and unauthenticated aside from the HMAC check.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the signed material, or otherwise cryptographically tie the header-derived identity to the verified body:
- Include `shop-domain` (and other trusted-but-unsigned headers the handler relies on) in `to_signable_string`, computing the HMAC the same way Shopify does if Shopify's HMAC scheme already covers headers via a canonicalized signing string, or
- Have `Registry.process` cross-check that the shop identified in the (verified) request matches an actual registered/active session shop before dispatching to the handler, rather than trusting the raw header unconditionally, and
- Document/enforce that consumers of `WebhookMetadata#shop` cannot treat it as cryptographically bound unless the gem itself verifies it.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and registers for a webhook topic (e.g. `customers/create`).
2. Shopify delivers a webhook to the app's endpoint with headers including `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid HMAC over raw body B>`, and body `B` (attacker fully controls the resource `B` describes, e.g. by creating a customer record with arbitrary content in their own store).
3. Attacker replays a POST to the same public endpoint with the identical raw body `B` and identical `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)` [6](#0-5)  which succeeds because it only recomputes the HMAC over `raw_body` using `Context.api_secret_key`, both of which are unchanged.
5. `WebhookMetadata` is constructed with `shop: request.shop` = `"victim-shop.myshopify.com"` and dispatched to the app's handler, which is misled into believing attacker-controlled data belongs to the victim shop. [7](#0-6)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** docs/usage/webhooks.md (L12-29)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
