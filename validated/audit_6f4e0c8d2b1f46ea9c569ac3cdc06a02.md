## Title
Webhook `shop` (tenant) identity is read from an unauthenticated header and is not covered by the HMAC signature, enabling cross‑tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`), `topic`, `webhook_id`, and `api_version` from raw HTTP headers, but the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw request body. The `shop` value that the registry later hands to the app's webhook handler is therefore never bound by the cryptographic signature, breaking the invariant `hmac_signed_content == shop_used_for_tenant_attribution`.

### Finding Description
`Request#hmac` and `Request#to_signable_string` define what is actually authenticated: [1](#0-0) [2](#0-1) 

`to_signable_string` returns only `@raw_body`. Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from headers with no cryptographic binding: [3](#0-2) 

`HmacValidator.validate` computes `HMAC-SHA256(secret, to_signable_string)` and compares it to the header-supplied signature — again, only the body bytes are covered: [4](#0-3) 

`Registry.process` then trusts `request.shop` (the unauthenticated header) to build the `WebhookMetadata` passed to the app's handler, which apps use to attribute the webhook payload to a specific tenant: [5](#0-4) [6](#0-5) 

The documentation explicitly tells app authors to key their persistence/attribution logic off `data.shop`: [7](#0-6) 

Because `shop` is never part of the signed bytes, any request whose **body** happens to carry a valid signature (i.e., any body that Shopify has genuinely signed for the app's `api_secret_key`, which is shared by the app across **all** shops it is installed on) can be replayed with an arbitrary `shopify-shop-domain` / `x-shopify-shop-domain` header. The signature check in `HmacValidator.validate` will still pass because it only re-derives the HMAC from `@raw_body`.

### Impact Explanation
This breaks tenant isolation (cross‑tenant access), one of the explicitly allowed Critical impacts. An attacker who controls one shop that has the app installed can:
1. Trigger a real webhook from their own shop with a body whose content is attacker-influenced (e.g., a webhook topic whose payload includes attacker-settable fields such as order/customer notes, product titles, or metafields), obtaining a body + a genuinely Shopify-issued HMAC signature.
2. Replay that exact `raw_body` + `hmac-sha256` header directly to the app's public webhook endpoint, substituting the `shopify-shop-domain` header with a victim shop's domain.
3. `HmacValidator.validate` accepts the request (only the body is checked), and `Registry.process` forwards `shop: <victim-domain>` to the app's handler, causing the app to process attacker-controlled data as if it originated from the victim tenant.

Depending on what the handler does with `data.shop` (e.g., look up/update the victim's stored session, cached product/order data, trigger tenant-scoped side effects, or process a mandatory GDPR topic like `customers/redact` against the wrong shop), this can corrupt or leak data across tenant boundaries — exactly the cross-tenant class of impact called out as Critical.

### Likelihood Explanation
Exploitation only requires: (a) attacker-owned/controlled shop installing the app to obtain one genuinely-signed webhook body, and (b) direct HTTP access to the app's public webhook endpoint (which by design must be internet-reachable to receive Shopify webhooks). No access to `api_secret_key`, access tokens, or TLS interception is required — this is a design gap in what the signature covers versus what the code treats as trusted identity, which is squarely a bug in this gem's `Request`/`HmacValidator` pairing rather than something requiring the host app to misuse a documented API.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the value that is verified, rather than trusting the header independently of the signature:
- Have the registry/handler cross-check `request.shop` against an out-of-band expectation (e.g., only accept webhooks for shops with an active, previously stored session/installation) before dispatching to the handler.
- At minimum, document/require that consuming apps treat `data.shop` as untrusted unless independently verified against known installed shops, since the HMAC does not, and cannot, authenticate it.

### Proof of Concept
1. Register the app on attacker-controlled `attacker-shop.myshopify.com`; trigger a webhook (e.g., `orders/create`) whose JSON body contains attacker-chosen content in a field the app's handler acts upon.
2. Capture the raw POST: body bytes `B` and header `X-Shopify-Hmac-Sha256: H` (genuinely computed by Shopify over `B` using the app's `api_secret_key`).
3. Send a new POST to the same app webhook endpoint with the identical body `B` and header `X-Shopify-Hmac-Sha256: H`, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and `X-Shopify-Topic`/`X-Shopify-Webhook-Id` as desired.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC from `request.to_signable_string` (`B`) — validation succeeds.
5. `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` is passed to the app's handler, which processes attacker-controlled body content under the victim shop's identity.

### Citations

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

**File:** docs/usage/webhooks.md (L12-26)
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
```
