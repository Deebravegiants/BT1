This confirms the root cause: `ShopifyAPI::Webhooks::Request` explicitly documents (docs/usage/webhooks.md line 125) that `Registry.process` "will verify the request did indeed come from Shopify" — but the verification (`Utils::HmacValidator.validate`) only covers `to_signable_string` (`@raw_body`), while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers and handed to the handler as trusted identity. This is the exact "field acted on but not covered by the HMAC" analog called out in the rules.

### Title
Webhook shop identity spoofing via HMAC that only covers the request body, not the `X-Shopify-Shop-Domain` header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0)  , so `Utils::HmacValidator.validate` only proves the request body was signed with the app's `api_secret_key` [2](#0-1) . The `shop` accessor, however, is read directly and unauthenticated from the `shopify-shop-domain`/`x-shopify-shop-domain` header [3](#0-2) , and `Registry.process` forwards that value straight to the app's handler as the authoritative tenant identity once HMAC validation "passes" [4](#0-3) .

### Finding Description
The equality this code is supposed to enforce is: `shop asserted to the handler == shop that the HMAC-signed bytes originated from`. In reality the HMAC binds only the raw JSON body, not the shop domain, topic, webhook id, or API version headers. Since `api_secret_key` is a single per-app secret shared across every merchant that installs the app (not a per-shop secret), any attacker who can get one authentic webhook delivery for a shop they control (e.g., by installing their own developer/test store with the target app, or simply observing any webhook payload+HMAC they legitimately received) possesses a `(raw_body, hmac)` pair that is valid under the app's secret regardless of which shop it is replayed as. The attacker can then re-POST the identical raw body and HMAC header to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header value. `HmacValidator.validate` will still succeed because it only recomputes the signature over `@raw_body` [5](#0-4) , and `Registry.process` will invoke the host app's handler with `shop: request.shop` set to the attacker-chosen value [4](#0-3) . The documentation explicitly tells integrators that `Registry.process` "will verify the request did indeed come from Shopify" [6](#0-5)  and that `data.shop` is "The shop domain of the webhook" [7](#0-6) , so app authors are led to trust it as an authenticated tenant identifier for downstream actions (e.g. looking up per-shop access tokens, writing shop-scoped records, enqueuing shop-scoped jobs as shown in the gem's own example: `perform_later(topic: data.topic, shop_domain: data.shop, ...)` [8](#0-7) ).

### Impact Explanation
This breaks the tenant boundary the gem is supposed to guarantee: cross-tenant access/confusion. A malicious merchant of the app can forge webhook events that appear to originate from a victim shop, causing the host application to process attacker-controlled webhook bodies under a victim shop's identity — for example, triggering shop-scoped side effects (writes, notifications, cache/job keys) attributed to the victim shop, or polluting per-shop data using another tenant's identifier while the actual signed payload came from the attacker's own store.

### Likelihood Explanation
Exploitation requires the attacker to possess valid Shopify credentials for at least one store running the app (trivial — install the app on any developer/partner test store, which is freely available) in order to receive one authentically-signed webhook. No access to `api_secret_key`, access tokens, or the victim's shop is needed; only the ability to replay an HTTP POST with a modified header. This is a realistic, low-effort attack path for any unprivileged user who can install the target app on their own store.

### Recommendation
Bind the shop identity (and ideally topic/webhook id/api version) into the signed material, or otherwise cryptographically verify that the `shop-domain` header corresponds to the shop the webhook was actually sent for — e.g., have `VerifiableQuery#to_signable_string` for `Webhooks::Request` include the shop domain header alongside the raw body, matching Shopify's documented webhook verification guidance, and reject/flag any mismatch. At minimum, document prominently that `data.shop` in `WebhookMetadata` is unauthenticated header data and must not be treated as verified without additional binding, and encourage host apps to cross-check it against the currently-registered shop context.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and registers for a webhook topic (e.g. `orders/create`).
2. Attacker triggers the webhook (e.g., creates an order) and captures the raw POST: body `B`, and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC-SHA256(api_secret_key, B)`), along with `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker replays the exact same request to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the signature over `B` only, which still matches `H`, so `Registry.process` calls the handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [9](#0-8) , causing the host app to process attacker-controlled data under the victim's tenant identity.

### Citations

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

**File:** docs/usage/webhooks.md (L12-14)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
