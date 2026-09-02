### Title
Webhook `shop` domain field is not covered by the HMAC signature, enabling cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's authenticity solely via `Utils::HmacValidator.validate(request)`, which computes the HMAC over `request.to_signable_string`. For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only `@raw_body`, while the `shop` value that is subsequently trusted and handed to the app's handler comes from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, which is never part of the signed bytes.

### Finding Description
The relevant code: [1](#0-0) 

`shop` is read directly from a header, but `to_signable_string` — the only input fed into the HMAC computation — returns just `@raw_body`: [2](#0-1) 

`Registry.process` performs exactly one authenticity check, `Utils::HmacValidator.validate(request)`, and if it passes, forwards `request.shop` — the unauthenticated header value — straight into `WebhookMetadata` given to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `to_signable_string`: [4](#0-3) 

The equality that should hold is: `shop_authenticated_by_hmac == shop_delivered_to_handler`. In this implementation, the left side does not exist — only the body is authenticated, while `shop` is parsed from a header outside the signed scope. Any two values of `shop` produce an identical, valid HMAC for the same body, so the binding is broken.

The documentation explicitly instructs developers to trust `data.shop` as the tenant identifier once `Registry.process` returns without raising: [5](#0-4) 

### Impact Explanation
An unprivileged actor who can install the app on their own (attacker-controlled) shop receives legitimate, correctly-HMAC-signed webhook deliveries for their own store's events (a developer/free store is sufficient to obtain this). Because the HMAC only covers `@raw_body`, the attacker can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` still succeeds (body and signature are unchanged), and `Registry.process` calls the handler with `shop: <victim-domain>` alongside the attacker's own webhook body. Any host application that follows this gem's documented pattern (using `data.shop` to select the tenant/session/database row to act on, as literally shown in the gem's own docs) will apply attacker-supplied data under the victim's tenant identity — a cross-tenant data-integrity/confusion issue reachable without any credentials beyond a normal app installation.

### Likelihood Explanation
High for any host application that follows the documented usage exactly as shown (`shop_domain: data.shop` used as a lookup key). Exploitation requires no `api_secret_key`, no access token, and no elevated privileges — only the ability to install the target app on any Shopify store (including free/dev stores) to receive one legitimately signed webhook, which is then replayed with a modified header at will (headers are attacker-controlled in an HTTP request and are not re-verified).

### Recommendation
Bind the `shop` (and ideally `topic`/`api_version`) header values into the HMAC-verified signable string, or independently verify the `shop` header against the shop associated with the webhook subscription (e.g., cross-checked via the registered webhook ID / stored session) before trusting it. At minimum, `Webhooks::Request#to_signable_string` should not be limited to the raw body if callers are expected to trust `shop` from an unauthenticated header.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST: body `B`, and header `x-shopify-hmac-sha256: H` (valid, computed by Shopify over `B` with the app's `client_secret`).
2. Replay the exact same body `B` and header `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but replace `x-shopify-shop-domain: attacker.myshopify.com` with `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac: H...})` is constructed; `to_signable_string` returns `B` unchanged.
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)` which recomputes `HMAC(B, secret)` and matches `H` — validation passes.
5. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's JSON>, ...)`, causing the host app (per documented usage) to process attacker-controlled data as belonging to `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
