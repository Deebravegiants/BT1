### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `Utils::HmacValidator` verifies binds *only* the body bytes to the app's `client_secret`. The `shop` value that the gem hands to app handlers (and that the docs explicitly tell developers to use as the tenant key) comes from the unauthenticated `X-Shopify-Shop-Domain` header, which is never part of the signed string.

### Finding Description
`Webhooks::Request` derives `shop` purely from a header: [1](#0-0) 

but its `to_signable_string` — the value that gets HMAC-verified — is only the raw body: [2](#0-1) 

`Registry.process` validates the request using exactly that signable string, and then forwards the untouched, HMAC-uncovered `request.shop` straight into the app handler's `WebhookMetadata`: [3](#0-2) 

`HmacValidator.validate` only compares `OpenSSL::HMAC.hexdigest(sha256, secret, to_signable_string)` against the supplied signature — it has no knowledge of, or binding to, the shop the payload claims to be from: [4](#0-3) 

The `client_secret` used to sign webhooks is the same for every merchant installation of a given app (it is the app-level secret, not a per-shop secret). Combined with the fact that many webhook topics have bodies that are shop-independent or fully attacker-observable (e.g. `app/uninstalled` has an empty `{}` body), an attacker who installs the app on their own shop receives a webhook whose `(raw_body, hmac)` pair is valid for *any* shop, because the signature never encodes which shop it came from. The gem's own documentation confirms `shop` is meant to be treated as an authoritative per-tenant field for scoping downstream work: [5](#0-4) 

The identity binding the code should enforce — `shop delivered in the HMAC-signed payload == shop the handler acts on` — is broken. In practice the equality that fails is:
`shop covered by HMAC (∅) != shop trusted by WebhookMetadata.shop (attacker-controlled header)`.

### Impact Explanation
This falls under "cross-tenant access": an unprivileged internet user who is themselves a legitimate installer of the target app (no special privileges, no leaked secrets required) can replay a genuine, validly-signed webhook body/HMAC pair captured from their own shop, while forging the shop-domain header to name a victim shop. Any app logic built on this gem's documented contract (using `data.shop` to select/scope tenant records, e.g. the doc's own example `perform_later(shop_domain: data.shop, webhook: data.body)`) will act on the victim tenant using attacker-supplied/attacker-observed data — e.g. triggering `app/uninstalled` cleanup, session teardown, or record updates against the victim shop's tenant scope instead of the attacker's own.

### Likelihood Explanation
Moderate-to-high: it requires only that the attacker (1) install the app on a shop they control (any developer/merchant can do this) and (2) know the target victim's `myshopify.com` domain (public information, easily discoverable). No access token, `client_secret`, or privileged credential is needed — the attacker only needs a body/HMAC pair that Shopify legitimately delivered to them.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed payload verification, or otherwise cryptographically bind the `shop-domain` header to the signature (e.g. verify shop against a server-side webhook-id/shop mapping obtained via the Admin API rather than trusting the header verbatim). At minimum, document that `data.shop` from `WebhookMetadata` is not authenticated by the HMAC and must not be used for tenant-scoping decisions without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Shopify sends a legitimate webhook (e.g. `app/uninstalled`, body `{}`) to the app's registered endpoint, signed with the app's shared `client_secret`:
   `X-Shopify-Hmac-Sha256: <valid-hmac-of-"{}">`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures the raw body (`"{}"`) and the valid `hmac` value from this delivery.
4. Attacker POSTs the same raw body and HMAC header to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Webhooks::Request.new` builds a request whose `hmac` still validates (`Utils::HmacValidator.validate`, per [6](#0-5) ), because the signature never covered `shop`.
6. `Registry.process` dispatches the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "app/uninstalled", body: {}, ...)`, causing the app to perform victim-tenant-scoped cleanup/side effects attributed to a shop the attacker never touched.

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
