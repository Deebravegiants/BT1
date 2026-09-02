### Title
Webhook shop-domain identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw HTTP body, while the `shop` (and `topic`/`webhook_id`) values that the library and its documented API treat as the trusted tenant identity are read directly from unauthenticated HTTP headers. Any party in possession of one valid `(body, hmac)` pair for the app's single, shop-agnostic `api_secret_key` can replay it with a different `shop-domain` header and have it accepted as authentic for a different merchant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers and are never included in the signed content: [2](#0-1) 

`HmacValidator.validate` only checks that `hmac` matches `HMAC(secret, to_signable_string)`, i.e. it only authenticates the body bytes, never the header-derived shop identity: [3](#0-2) 

`Webhooks::Registry.process` validates the HMAC and then unconditionally trusts `request.shop` (and `request.topic`) to build the data passed to the app's handler: [4](#0-3) 

The gem's own documentation instructs integrators to treat `data.shop` as the authoritative per-tenant identifier for dispatching downstream work (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), so this is not a misuse of an undocumented API — it is the documented usage pattern: [5](#0-4) 

The identity binding broken here is: **shop domain authenticated by the signature == shop domain the handler is told to act on**. Before the attack, this equality holds only incidentally, because Shopify's own servers set the header. After the attack (an attacker replaying a captured, validly-HMAC'd body with a substituted `shop-domain` header), the equality is false: the HMAC still validates (it never covered the header), but `request.shop`/`data.shop` now names a different, victim tenant than the one that actually produced the signed bytes.

Critically, `api_secret_key` is a single shared secret configured once per app (via `ShopifyAPI::Context.setup`) — not per-installed-shop. Any merchant who installs the app receives genuine webhooks signed with that same app-wide secret. Such a merchant (an "unprivileged internet user" from the perspective of any other tenant of the app) can capture one of their own legitimate webhook deliveries (raw body + `X-Shopify-Hmac-Sha256` value) and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop that also uses the same app. `HmacValidator.validate` will accept it because only the body is checked, and `Registry.process` will invoke the app's handler with `shop` set to the victim's domain and `body` set to the attacker's own (attacker-controlled) webhook payload.

### Impact Explanation
This breaks tenant isolation between merchants of the same app (cross-tenant access), which is explicitly listed as a Critical impact category. Depending on the topic the attacker chooses to replay (which is likewise unauthenticated), this can be used to inject attacker-controlled data into another shop's tenant record (e.g., fabricated `orders/create`, `customers/create` payloads attributed to the victim shop) or to trigger sensitive lifecycle webhooks such as `app/uninstalled` against a victim shop the attacker does not own, causing the app to purge/deactivate that victim's stored session and data.

### Likelihood Explanation
Likelihood is realistic for any app built on this gem that follows its documented webhook pattern: the attacker only needs their own legitimate installation of the target app (to receive one authentic signed webhook) and network access to the app's public webhook endpoint — no access to `api_secret_key`, tokens, or any privileged account for the victim shop is required. The attack does not depend on secret leakage; it exploits the gem's failure to bind the authenticated bytes to the shop-domain header the gem itself teaches developers to trust.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-signed content, or independently bind/verify the `shop-domain` header against known/expected values (e.g., cross-check against the shop associated with the webhook subscription, or require a per-shop signing context) before exposing `request.shop`/`WebhookMetadata#shop` to handlers. At minimum, document prominently that `data.shop` is not authenticated by the HMAC and must not be used as a sole tenant key without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, so the app's shared `api_secret_key` is used to sign webhooks delivered to them.
2. Shopify delivers a legitimate webhook to the app, e.g.:
   - Headers: `X-Shopify-Topic: orders/create`, `X-Shopify-Hmac-Sha256: <valid-hmac>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - Body: `{"id": 1, ...attacker-controlled order fields...}`
3. Attacker captures the raw body and the `X-Shopify-Hmac-Sha256` value (both are visible to them as the shop owner/recipient of the webhook, or via any proxy they control).
4. Attacker POSTs the exact same raw body and `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Webhooks::Request#to_signable_string` returns the unchanged raw body, so `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds.
6. `Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb`) invokes the registered handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`.
7. The app processes attacker-controlled data as though it came from `victim-shop.myshopify.com`, per the documented handler pattern in `docs/usage/webhooks.md`.

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
