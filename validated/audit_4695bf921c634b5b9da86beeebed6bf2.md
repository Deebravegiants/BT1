### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, while the `shop` (tenant) identifier is taken from an HTTP header that is never included in that signature. This breaks the identity binding `shop authenticated-by-HMAC == shop trusted-by-handler`, letting a merchant who legitimately receives a webhook for their own store re-attribute that same (validly-signed) payload to a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook using only `Utils::HmacValidator.validate(request)`: [1](#0-0) 

The HMAC computed by `HmacValidator` is over `verifiable_query.to_signable_string`: [2](#0-1) 

For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns **only the raw body** (`@raw_body`), while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from HTTP headers that are completely outside the signed material: [3](#0-2) 

After the HMAC check passes, `request.shop` is handed directly to the registered handler as trusted tenant identity via `WebhookMetadata`: [1](#0-0) 

Documentation confirms `data.shop` is meant to be trusted as "The shop domain of the webhook" and is expected to be used directly by host apps (e.g., to look up sessions or route work) without further validation: [4](#0-3) 

Because the API secret key used to compute the HMAC is the app's single `client_secret` (shared across every shop that installs the app), any merchant who installs the app can obtain a genuinely Shopify-signed webhook body+HMAC pair for their **own** shop. Since the `shop-domain` header is not part of the signed content, that same body/HMAC can be replayed to the app's webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header rewritten to any other shop's domain. `Utils::HmacValidator.validate` will still return `true` (the body and HMAC are unchanged and valid), and the handler will process the event believing it originated from the victim shop.

### Impact Explanation
This is a cross-tenant identity-binding failure: the equality that should hold, `hmac_signed_shop == request.shop_used_by_handler`, does not hold because `shop` is never part of the signed payload. An attacker (any merchant who has installed the app, i.e., an "unprivileged" tenant relative to other tenants) can forge webhook events attributed to a different shop, potentially triggering shop-scoped side effects in the host application (e.g., app/uninstalled handling, order processing state changes, session/data operations keyed by `shop`) under a shop the attacker does not control. This matches the "cross-tenant access" criterion for Critical impact.

### Likelihood Explanation
The attacker only needs: (1) their own instance of the app installed (readily available to anyone who can install a public/embedded app), and (2) the ability to send an HTTP POST to the app's public webhook endpoint with custom headers — both trivial for any external, unprivileged user. No access token, `client_secret`, or privileged credentials are required, since a legitimately-received webhook for the attacker's own shop already carries a valid HMAC.

### Recommendation
Include the shop domain (and ideally the topic and webhook id) in the value that is HMAC-verified, or otherwise cryptographically bind the header-derived `shop` to the signed body — for example by validating the shop against a per-shop registered webhook secret/session, or refusing to trust the `shop-domain` header unless it is corroborated by an independent authenticated source. At minimum, document and enforce that host applications must not use `data.shop` as the sole tenant key without further verification (e.g., cross-checking against the shop that is expected to receive events for a subscribed handler).

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook event (e.g. `orders/create`) so Shopify sends a POST with body `B` and header `x-shopify-hmac-sha256: HMAC(B, client_secret)` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Capture this legitimate request.
3. Replay the exact same body `B` and HMAC header to the app's webhook endpoint, but change `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `@raw_body` (`B`) — unchanged — so validation succeeds.
5. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the host app to act on data intended only for the attacker's shop as though it belongs to the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
