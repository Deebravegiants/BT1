## Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are not covered by the HMAC signature, allowing cross-tenant shop-spoofing replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC computed over the raw request **body**, then hands the caller's application handler a `WebhookMetadata` struct whose `shop` (tenant identity), `topic`, and `webhook_id` fields are read straight from unauthenticated HTTP headers that are never included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) that are completely independent of the signed payload: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which — per `HmacValidator#validate_signature` — computes `HMAC(secret, request.to_signable_string)` (i.e., only the body) and compares it to the `hmac` header. It never checks that the `shop` header (or `topic`/`webhook_id`) is bound to that HMAC: [3](#0-2) [4](#0-3) 

The identity binding the library implicitly claims to the host application is: `hmac_valid? == true` implies `(shop, topic, webhook_id, body)` all genuinely originated from Shopify for that shop. In reality the equality only holds for `body`:

`HMAC(secret, body) == received_hmac` — proves only `body` is untampered and secret-known.
`shop header == shop that generated this webhook` — **not proven**, because `shop` is outside the signed bytes.

The documentation instructs developers to trust `data.shop` from the resulting `WebhookMetadata` as the shop identity for the event, with no guidance to independently verify it against an installed-shop list: [5](#0-4) [6](#0-5) 

**Exploit path (no `client_secret` needed):** An unprivileged internet user who can install the target app on their own store (Shop A) will legitimately receive a genuinely-Shopify-signed webhook whose HMAC is valid for a given body (e.g., an `orders/create` payload). Because the HMAC is computed only over the body — not over the shop, topic, or webhook_id headers — the attacker can capture that single valid `(body, hmac)` pair from their own shop and replay it to the app's webhook endpoint with the `shopify-shop-domain` header (and/or `shopify-topic`/`shopify-webhook-id`) rewritten to reference a victim shop. `Utils::HmacValidator.validate` still returns `true` because it only recomputes the HMAC over the unchanged body, and `Registry.process` forwards the attacker-chosen `shop` value straight into the handler as authenticated tenant context.

### Impact Explanation
This breaks the cross-tenant boundary the library is meant to enforce for webhook processing: a valid HMAC does not guarantee the `shop` (or `topic`/`webhook_id`) reported to the host application is authentic. A host app that (reasonably, given the documented API and the fact that `process` already "verifies the request did indeed come from Shopify") trusts `data.shop` to select which tenant's data/queue/DB row to update will process attacker-supplied events under another shop's identity — i.e., cross-tenant data confusion/injection using only a webhook payload the attacker legitimately received for their own shop. This matches the Critical/High "cross-tenant access" impact criterion.

### Likelihood Explanation
Any merchant/developer who can install the app on a store they control can obtain a validly-signed webhook body+hmac pair for arbitrary supported topics (they control the actions that trigger webhooks, e.g. creating their own order/product). Replaying that captured `(body, hmac)` with a modified `shop`/`topic`/`webhook_id` header requires no secret material and no privileged access — only the ability to send an HTTP POST to the app's public webhook endpoint, which is by definition internet-reachable. The severity of consequences depends on how permissively the host app trusts `data.shop`, which the gem's own documentation encourages (`data.shop` is presented as reliable webhook metadata with no caveat).

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or at minimum `shop`) in the bytes that are HMAC-verified, or otherwise cryptographically bind them to the request (e.g., verify `shop` against the session/shop that originally installed the app and against which the webhook subscription was registered) before constructing `WebhookMetadata`. At minimum, document prominently that `HmacValidator` only authenticates the raw body and that `shop`/`topic`/`webhook_id` headers must be independently verified by the host application against its own known-shops list before being trusted as tenant identity.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`, triggers an `orders/create` event, and captures the resulting legitimate webhook POST — headers `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, body `B`.
2. Attacker resends the exact same body `B` and `x-shopify-hmac-sha256: H` to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "x-shopify-shop-domain" => "victim-shop.myshopify.com"})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and compares to `H` — this matches because `B` and `H` are unchanged, per `hmac_validator.rb` lines 26-31.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: B, ...)`, per `registry.rb` lines 198-199 — the host application now processes attacker-controlled order data under the victim shop's identity, despite the HMAC check having "passed."

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L10-30)
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
    end
  end
end
```
```
