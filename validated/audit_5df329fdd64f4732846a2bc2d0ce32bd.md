### Title
Webhook `shop` domain is trusted for tenant identification but is excluded from the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the HMAC only over the raw request body, while the `shop` (tenant identifier) is read from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header and passed downstream to webhook handlers as trusted tenant context.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Request#shop` reads directly from `shopify_header("shop-domain")` with no cryptographic binding to that value: [1](#0-0) 

`HmacValidator.validate` verifies the HMAC exclusively against `to_signable_string`, i.e. the body bytes, never the `shop` header: [2](#0-1) 

`Registry.process` validates only that HMAC-over-body, then forwards `request.shop` straight into `WebhookMetadata` handed to the app's handler as the tenant/shop context for the delivered body: [3](#0-2) 

`WebhookMetadata.shop` is documented and typed as an authoritative field the handler is expected to use to route/attribute data to a shop: [4](#0-3) [5](#0-4) 

The identity binding the code implicitly claims is: `hmac_valid(body, secret) == true` implies `(body, shop)` is an authentic tuple from Shopify for that shop. In reality the equality only holds for `body`; `shop` is unauthenticated header data disjoint from the signed content, exactly the same class of break as the report's mismatched-selector bug where a value acted upon (`mintAmount`) was not actually covered/matched by the verification mechanism (the selector).

### Impact Explanation
Any unprivileged internet client that has ever received one legitimate webhook delivery for its own installed shop (a completely non-privileged action — anyone can install a Shopify dev/free-trial shop and receive its own webhooks) can capture a `(raw_body, hmac)` pair that is valid under the app's `api_secret_key`, then replay it with an arbitrary `x-shopify-shop-domain` header pointing at a victim (different tenant) shop. Since `HmacValidator.validate` never looks at the `shop` header, the forged request passes validation and the handler is invoked with attacker-chosen `body` content and an attacker-chosen victim `shop` value. Any host application that follows the documented pattern (using `data.shop` to select which tenant record/session/queue job the payload applies to — as shown in the gem's own webhook docs example, `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) will process attacker-controlled data under the wrong tenant's identity — a cross-tenant data injection/spoofing condition that meets the "cross-tenant access" Critical impact bar.

### Likelihood Explanation
High for any app that follows the gem's own documented usage pattern (using `WebhookMetadata#shop` as the tenant key for background processing), since obtaining one valid `(body, hmac)` pair only requires installing the app on any shop the attacker controls — no leaked secret, no privileged account, and no interception is required, satisfying the in-scope threat model of an unprivileged internet user.

### Recommendation
Include the shop domain (and other identity-relevant headers, e.g. `topic`, `webhook_id`) inside the signed material verified by `HmacValidator`, or otherwise re-derive/cross-check the shop identity from a source bound to the signature (e.g. correlate `webhook_id`/subscription registration to an expected shop) rather than trusting the raw header value. At minimum, update `docs/usage/webhooks.md` to explicitly warn that `WebhookMetadata#shop` is unauthenticated and must not be used as a tenant boundary without additional verification.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own shop "attacker.myshopify.com"
#    and captures a legitimate webhook delivery, e.g. for orders/create:
raw_body = '{"id":1,"note":"legit order"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)

# 2. Attacker replays the exact same body+hmac but swaps the shop-domain header
forged_headers = {
  "x-shopify-topic"        => "orders/create",
  "x-shopify-hmac-sha256"  => Base64.encode64(valid_hmac),
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # arbitrary, unverified
  "x-shopify-webhook-id"   => "any-id",
  "x-shopify-api-version"  => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# 3. Passes HMAC validation because only raw_body is signed/verified:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# 4. Registry.process forwards forged shop into the handler as trusted tenant context:
ShopifyAPI::Webhooks::Registry.process(request)
# handler.handle(data: WebhookMetadata(shop: "victim-shop.myshopify.com", body: {...}, ...))
```

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
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
