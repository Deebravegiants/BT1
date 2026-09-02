### Title
Webhook `shop` and `topic` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats an inbound HTTP webhook as authentic for whatever shop is named in the `shopify-shop-domain`/`x-shopify-shop-domain` header once `Utils::HmacValidator.validate` passes, but the HMAC only ever covers the raw body — never the `shop`, `topic`, or `webhook-id` headers that the handler is given as the trusted identity of the event.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` and `topic` are read straight from attacker-suppliable HTTP headers, with no cryptographic tie to the body that was actually HMAC-signed: [2](#0-1) 

`Registry.process` validates only the HMAC over the signable string and then immediately dispatches to the handler using the unverified `request.shop`/`request.topic`: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the raw body) and the app's shared `api_secret_key`, which is identical for every shop that has installed the app: [4](#0-3) 

Because the secret is shared across all merchants of an app (not shop-specific), an attacker who installs the app on their own store receives genuine, validly-signed webhooks (`raw_body` + `hmac`) for their own shop. The HMAC only binds the body; it never binds `shop-domain` or `topic`. The attacker can therefore take a legitimately-signed `(body, hmac)` pair and resubmit it directly to the app's public webhook endpoint with the `shop-domain` header rewritten to a victim shop and/or the `topic` header rewritten to a different topic. `Utils::HmacValidator.validate` still returns `true` (the body/hmac pair is valid), and `WebhookMetadata` is built with the attacker-chosen `shop`/`topic`, which the host application uses to route the payload as if it originated from the victim shop.

This is the exact "field acted on but not covered by the HMAC" identity-binding break called out in the audit rules — the docs explicitly tell app authors to trust `data.shop`/`data.topic` as authoritative identity for the event: [5](#0-4) 

Equality that should hold but doesn't: `shop_covered_by_hmac == shop_used_by_handler`. In reality, `shop_covered_by_hmac = ∅` (not present in `to_signable_string`) while `shop_used_by_handler = header["shopify-shop-domain"]`, fully attacker-controlled.

### Impact Explanation
Any app built on this gem that keys business logic (session lookup, data writes, uninstall/GDPR handling, billing state, etc.) off `WebhookMetadata#shop` or `#topic` as delivered by this library can be made to process attacker-forged events under a victim shop's identity, using only a validly-signed body the attacker obtained from their own (attacker-owned) shop installation. This is a cross-tenant identity confusion vector reachable by any unprivileged internet user who can install the app once on a store they control and can reach the app's public webhook HTTP endpoint — satisfying the "cross-tenant access" Critical-impact category in the rules.

### Likelihood Explanation
Likelihood is High for apps that expose the webhook path publicly (a documented requirement for HTTP webhook delivery) and trust `data.shop`/`data.topic` as-is, since the gem's own documentation instructs developers to do exactly that. The attacker needs no privileged credentials, no `api_secret_key`, and no access token — only their own legitimate app installation to harvest one valid `(body, hmac)` pair, plus the ability to send an arbitrary HTTP request to the app's webhook endpoint (headers are fully attacker-controlled once outside Shopify's own delivery infrastructure).

### Recommendation
Include `shop-domain`, `topic`, and `webhook-id` in the HMAC-signed material (or otherwise cryptographically bind them to the body), or require the host application to validate `shop`/`topic` against an out-of-band trusted source (e.g., the registered callback path per topic/shop) before trusting `WebhookMetadata`. At minimum, document prominently that `shop`/`topic` are unauthenticated header values and must not be trusted without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) with attacker-chosen JSON body content.
2. Shopify delivers the webhook to the app's public endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid hmac of body>`.
3. Attacker replays the same `raw_body` and `hmac` header value directly to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers/body; `Utils::HmacValidator.validate` returns `true` because the HMAC only covers `raw_body`, which is unchanged (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:12-31`).
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: <attacker body>, ...)` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the host app to act on victim-shop data/session using attacker-controlled content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** docs/usage/webhooks.md (L12-30)
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
```
