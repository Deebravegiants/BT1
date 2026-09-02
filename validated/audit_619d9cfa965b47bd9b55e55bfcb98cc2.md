This confirms the root cause: `Utils::VerifiableQuery` is an interface requiring only `hmac` and `to_signable_string`. For webhooks, `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read from an unsigned header [2](#0-1) . `Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` against the HMAC [3](#0-2) , so the `shop` value is never bound to the signature. `Registry.process` nonetheless treats `request.shop` as trusted tenant identity and forwards it straight to the app's handler [4](#0-3) , and the docs explicitly promise this call "will verify the request did indeed come from Shopify" [5](#0-4)  and that the resulting `data.shop` is safe to use as "The shop domain of the webhook" [6](#0-5) .

### Title
Webhook `shop` domain is not covered by HMAC verification, allowing cross-tenant impersonation - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity using `Utils::HmacValidator.validate`, which computes the HMAC only over the request body (`to_signable_string` returns `@raw_body`). The `shop` domain — the value used by the gem and, per its own documentation, by the host app to identify which tenant the webhook belongs to — comes from the `x-shopify-shop-domain` / `shopify-shop-domain` header and is never included in the signed payload. Since the app's `api_secret_key` is shared across all shops that install the app, any shop with a legitimate installation can capture a validly-signed webhook it receives and replay it to the app's webhook endpoint with the `shop-domain` header swapped to a different (victim) shop. The HMAC check still passes because the header is outside the signed bytes, breaking the equality `shop authenticated by HMAC == shop acted upon by the handler`.

### Finding Description
`Webhooks::Request` extracts `shop` purely from headers [2](#0-1)  and defines `to_signable_string` to return only the raw body [1](#0-0) . `HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the supplied HMAC [3](#0-2)  — the `shop` header plays no role in this computation. `Registry.process` gates on this HMAC check and then unconditionally builds `WebhookMetadata` from `request.shop` for the handler to consume [4](#0-3) .

Because the app's `api_secret_key` is a single per-app secret shared across every shop that installs the app (not a per-shop secret), a merchant who legitimately installs the app on Shop A receives real, validly-HMAC-signed webhook deliveries for Shop A. That merchant can capture such a delivery and re-POST it to the app's public webhook endpoint after altering only the `x-shopify-shop-domain` header to Shop B's domain. `Utils::HmacValidator.validate` still returns `true` because the raw body (and hence the signature) is unchanged; `request.shop` now falsely reports Shop B. The equality that should hold — "the shop bound by the HMAC" == "the shop the handler acts on" — is broken: the HMAC binds nothing about shop identity, yet `Registry.process` and the documented `WebhookHandler#handle(data:)` contract treat `data.shop` as an authenticated tenant identifier [7](#0-6) .

### Impact Explanation
This is a cross-tenant identity-binding break: an attacker who is a legitimate but unprivileged user of the multi-tenant app (installer on their own store) can forge webhook events that the host application will attribute to any other shop of their choosing, while still passing this gem's documented authenticity check. Depending on how the host app uses `data.shop` (as most apps do, per the gem's own example — `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [8](#0-7) ), this enables injecting attacker-chosen data (orders, product updates, GDPR payloads, app-uninstalled events, etc.) into another merchant's tenant record — cross-tenant access/data corruption.

### Likelihood Explanation
Moderate-to-high: exploitation only requires the attacker to be able to install the target app on a store they control (a normal, unprivileged action available to anyone) and capture one legitimate webhook delivery from Shopify. No access to `api_secret_key`, tokens, or victim credentials is required — only replay of the captured payload with a modified header value.

### Recommendation
Bind the shop identity to the signed payload before trusting it: verify `request.shop` against the shop associated with the specific webhook subscription/session that was registered (e.g., cross-check `webhook_id`/`shop` against records stored at registration time in `Registry.register`), or otherwise require the host app to independently confirm shop ownership of the webhook_id before acting on `data.shop`. At minimum, document prominently that `data.shop` is unauthenticated and must not be used as a sole tenant key without additional verification, since the current docs (`docs/usage/webhooks.md`) imply the opposite.

### Proof of Concept
1. Attacker installs the app normally on `attacker-shop.myshopify.com`, obtaining a legitimate installation with the shared `api_secret_key`.
2. Shopify sends a real webhook to the app, e.g. `topic: orders/create`, body `B`, headers including `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this request and replays it to the same webhook endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com` (HMAC header and body `B` unchanged).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which recomputes the HMAC over `B` only [9](#0-8)  and finds it matches — validation succeeds.
5. `Registry.process` invokes the host handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: B, ...)` [10](#0-9) , causing the host app to process attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
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
