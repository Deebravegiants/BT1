This confirms the finding: `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` only signs `verifiable_query.to_signable_string`, and `Webhooks::Request#to_signable_string` in `lib/shopify_api/webhooks/request.rb` returns only `@raw_body`. The `shop` value returned by `Request#shop` (parsed straight from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header) is never included in the signed material, yet `Registry.process` forwards it unchecked as the tenant identity into `WebhookMetadata`, which the docs (`docs/usage/webhooks.md`) explicitly tell integrators to key their per-shop side effects on.

### Title
Webhook shop-domain header is excluded from HMAC signing, allowing cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` (used by `Utils::HmacValidator.validate`) signs only the raw webhook body. The `shop` accessor is read straight from the `x-shopify-shop-domain` header, which is never part of the HMAC-covered material. `Registry.process` trusts this unauthenticated header value as the tenant identity passed to the app's `WebhookHandler`.

### Finding Description
`Registry.process` validates a webhook exclusively via:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
``` [1](#0-0) 

`Utils::HmacValidator.validate_signature` computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For webhooks, `to_signable_string` is defined as only the raw body:
```ruby
def to_signable_string
  @raw_body
end
``` [3](#0-2) 

Meanwhile `shop` is read directly from the untrusted `shop-domain` header:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [4](#0-3) 

After HMAC validation succeeds (which only proves the *body* bytes were signed by Shopify with the app's secret), `Registry.process` binds the *unverified* `request.shop` value into the `WebhookMetadata` handed to the app's handler:
```ruby
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
``` [5](#0-4) 

The equality that the gem's HMAC check should establish is: `shop-that-triggered-the-webhook == shop-passed-to-the-handler`. Instead, the gem only establishes `body-bytes-signed-by-Shopify == body-bytes-received`. The `shop` binding is absent. The gem's own documentation confirms `shop` is meant to identify "The shop domain of the webhook" and tells integrators to key per-tenant side effects on it directly (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), reinforcing that this field is trusted as an authenticated tenant identifier by design. [6](#0-5) 

### Impact Explanation
Any entity capable of causing a legitimate, HMAC-valid webhook body/signature pair to exist for the app (e.g. a merchant who has installed the app on their own store and triggers webhook deliveries with predictable/fixed bodies, such as `shop/redact`, `customers/redact`, `app/uninstalled`, or any topic whose payload doesn't itself contain shop-identifying content) can replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` still passes because it never inspects the header, and `Registry.process` then invokes the app's handler claiming the event is `shop: <attacker-chosen-value>`. Depending on how the host application's `WebhookHandler` implementation uses `data.shop` (as instructed by this gem's own documentation) — e.g. to look up the tenant's session/access token, delete tenant data for GDPR redaction, or deactivate/uninstall the app for that tenant — this enables cross-tenant data manipulation or denial of service against a shop the attacker does not control, without needing the app's `api_secret_key` or any tenant's access token.

### Likelihood Explanation
Exploitability depends on the host application's webhook handler trusting `data.shop` for tenant-scoped actions, which is exactly the pattern this gem's documentation recommends. It further requires the attacker to obtain at least one valid `(raw_body, hmac)` pair, which is achievable without secrets whenever a webhook topic's body content is deterministic/low-entropy (mandatory topics like `shop/redact`, `customers/redact`, `customers/data_request`, or `app/uninstalled`), since the attacker can generate that pair legitimately from their own store's webhook delivery and replay it with a forged shop header.

### Recommendation
Bind the shop domain (and other identifying headers such as topic/webhook-id) into the HMAC-signed material, or otherwise verify `request.shop` out-of-band against a value already associated with the specific webhook subscription/access token before trusting it in `WebhookMetadata`. At minimum, document prominently that `data.shop` in `WebhookMetadata` is *not* cryptographically authenticated by the HMAC check and must not be used alone to select tenant secrets or perform destructive tenant-scoped actions without additional verification (e.g. cross-checking against a shop record you already control for that webhook subscription).

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook for a mandatory/low-entropy topic (e.g. `shop/redact`) with raw body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC computed by Shopify over `B` using the app's secret).
2. Attacker replays the exact same request to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`== B`, unchanged) and finds it matches `H` — validation succeeds, since `shop` is never part of the signed string: [3](#0-2) 
4. `handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...))` is invoked, and the host app processes the event as if it originated from `victim-shop.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
