### Title
Webhook `shop-domain` header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that is read directly from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, but the HMAC signature validated by `ShopifyAPI::Webhooks::Registry.process` only covers the raw request body, never the headers. Any unprivileged internet user who has captured one genuine webhook delivery (e.g. by installing the target app on their own store and triggering a webhook with an identical body, such as `app/uninstalled` or any topic whose payload is not shop-specific) can resend that exact `raw_body`/HMAC pair to the app's public webhook endpoint while substituting an arbitrary victim shop domain in the `shop-domain` header. `Registry.process` will still consider the HMAC valid and will dispatch the handler with the attacker-chosen `shop`, breaking the binding: `hmac-signed bytes == raw_body` while `tenant identity == unauthenticated shop header`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` value used by consumers of the webhook is taken straight from the request headers with no cryptographic linkage to the signed content: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then forwards `request.shop` (the unauthenticated header value) straight into the handler as the tenant identity for the webhook: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` confirm this: the signature is computed and compared against `verifiable_query.to_signable_string`, which for `Request` is just the raw body, never the shop header: [4](#0-3) 

Because the signature never binds to the `shop-domain` header, any HTTP request with a previously-observed valid `(raw_body, hmac)` pair — trivially obtainable by the attacker triggering a webhook on their own shop, since the same app `api_secret_key` is shared across all installs of that app — can be replayed against the app's public webhook endpoint with the `shop-domain` header rewritten to any victim shop. `Registry.process` will accept it as authentic and hand the forged `shop` value to the app's webhook handler as though it originated from that victim tenant.

### Impact Explanation
This is a cross-tenant identity confusion in the webhook trust boundary that this gem itself establishes and documents (`ShopifyAPI::Webhooks::Registry.process` is the exact call recommended in `docs/usage/webhooks.md` for verifying "the request did indeed come from Shopify"). Any host application that uses `WebhookMetadata#shop` (as returned by `process`) to scope data lookups/writes — the intended and documented usage — can be made to act on the wrong merchant's tenant data, since the gem asserts the request is authentic for the header-supplied shop when in fact only the body is authenticated. This meets the Critical bar of cross-tenant access via an authentication-boundary violation of the gem's own HMAC guarantee.

### Likelihood Explanation
Any internet user can become an app installer on their own development/test store to legitimately trigger a webhook and capture a valid `(raw_body, hmac)` pair for a topic whose payload carries no shop-specific data (or is otherwise indistinguishable across shops), then POST that identical body/HMAC directly to the app's public webhook URL with a different `shop-domain` header. No access token, `client_secret`, or privileged account is required — only observation of one's own legitimately delivered webhook and the ability to send an unauthenticated HTTP POST to the app's endpoint.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed material that `HmacValidator` verifies, or independently re-derive/verify the shop identity (e.g. cross-check `shop-domain` against a shop known from an already-established session/webhook registration, or include the header values in the signable string as Shopify actually intends `X-Shopify-Hmac-Sha256` to validate the full canonical payload including topic/shop). At minimum, document/enforce that consumers must not trust `WebhookMetadata#shop` as tenant-authenticated unless it is cross-verified against another authenticated source.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook whose body is shop-agnostic or shared in structure (e.g. `app/uninstalled`), capturing the exact `raw_body` and the corresponding `x-shopify-hmac-sha256` value that Shopify sent.
3. Attacker POSTs that identical `raw_body` and `hmac` to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC — it never inspects the `shop-domain` header.
5. The registered handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and any app logic keyed on that `shop` value now operates as if the event came from the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
