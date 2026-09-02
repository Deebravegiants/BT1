This confirms the vulnerability. The `shop-domain` header is read directly by `ShopifyAPI::Webhooks::Request#shop` [1](#0-0)  but the HMAC signature in `to_signable_string` only covers `@raw_body`, never the headers [2](#0-1) . `Registry.process` validates the HMAC over the request, then constructs `WebhookMetadata` directly from the unauthenticated `request.shop` and hands it to the app's handler as the tenant identifier [3](#0-2) . The docs explicitly instruct integrators to trust `data.shop` as the shop domain for the webhook [4](#0-3) .

### Title
Webhook `shop` (tenant identifier) is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values are taken from HTTP headers that are entirely outside the HMAC's coverage. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant/store identifier passed to the app's handler. This breaks the intended binding: `HMAC-verified-shop == shop-used-for-tenant-routing`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [2](#0-1) . `Request#shop` is read straight from the `X-Shopify-Shop-Domain`/`Shopify-Shop-Domain` header without any cryptographic binding to the body or its HMAC [1](#0-0) . `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `request.to_signable_string` (the raw body) against `request.hmac` [5](#0-4) . It then builds `WebhookMetadata` using the same unauthenticated `request.shop` header value and forwards it to the app's handler [3](#0-2) .

Because the HMAC is computed only over the body, any two webhook deliveries with identical body content (which commonly occurs across topics/shops using this gem, e.g., repeatable/templated payloads, or an attacker who is a legitimate app installer on their own shop capturing their own genuinely-signed webhook) produce an HMAC that remains valid regardless of which shop-domain header accompanies it. An attacker who controls one tenant (their own store where the app is installed, i.e., an "unprivileged" party with respect to other tenants) can capture a validly-HMAC-signed webhook body from their own shop and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop's domain. `HmacValidator.validate` will pass because it only checks the body/HMAC pair, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the victim shop, despite the payload never having been signed as belonging to that shop.

This is the direct analog of the reported bug class: a field (`to`/msg.sender in the original report; here, `shop`) is acted upon by downstream logic but is not actually covered by the authentication/integrity check (`mimicCall` register reuse in the original; HMAC-over-body-only here), letting an attacker substitute an unauthenticated value while reusing a validly-authenticated wrapper.

### Impact Explanation
This enables cross-tenant confusion: an app relying on `data.shop` from `WebhookMetadata` (as the gem's own documentation instructs integrators to do) to select which merchant's session/data to act on can be made to process a legitimately-signed payload under an attacker-chosen shop identity. Depending on the topic (e.g., `app/uninstalled`, `shop/redact`, `customers/data_request`, or any webhook whose body content can coincide across shops), this can cause the host application to update state, delete data, or trigger tenant-scoped side effects for a shop the attacker does not own — a cross-tenant access impact.

### Likelihood Explanation
Exploitability requires the attacker to have their own legitimate (even trial) app installation to obtain a validly-signed webhook, and for a webhook payload's content to be reproducible/predictable or independent of shop-specific data (many webhook bodies for a given topic have identical or highly-predictable JSON shape/content across shops, especially those with empty or template-fixed bodies as shown in this gem's own tests, e.g., `raw_body: "{}"`). No access token, `api_secret_key`, or privileged access is required — only the ability to send an HTTP POST to the app's public webhook endpoint with a captured HMAC/body pair and a forged shop header.

### Recommendation
Bind the `shop` (and `topic`/`webhook_id`/`api_version`) values into the HMAC-verified signable content, or otherwise cryptographically tie the header-supplied shop domain to the payload before trusting it for tenant identification. At minimum, the gem should document/warn that `data.shop` in `WebhookMetadata` is not covered by HMAC verification and must not be used as an authoritative tenant identifier without additional validation (e.g., cross-checking against a known/registered shop for that webhook subscription).

### Proof of Concept
1. App A (attacker-controlled) installs the target Shopify app; Shopify sends a legitimate webhook to the app's endpoint with body `B` (e.g., `"{}"` for a topic with an empty payload) and headers including `X-Shopify-Shop-Domain: attacker-shop.myshopify.com` and a valid `X-Shopify-Hmac-Sha256` computed over `B` with the app's `client_secret`.
2. Attacker captures this raw request (body `B` + valid HMAC header).
3. Attacker resends the same body `B` and HMAC header to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) succeeds because it only checks `B` against the HMAC.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and invokes the app's handler, which — per the gem's documented usage pattern — trusts `data.shop` as the authoritative tenant for this webhook event.

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

**File:** docs/usage/webhooks.md (L10-26)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
