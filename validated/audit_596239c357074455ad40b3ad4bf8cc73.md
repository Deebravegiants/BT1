## Finding: Webhook `shop` identity is not covered by the HMAC signature

The webhook processing path validates only the raw request body against the HMAC, but hands the caller-supplied `shop-domain` header — which is *not* part of the signed material — as the trusted tenant identifier to the webhook handler.

### Root cause

`ShopifyAPI::Webhooks::Request` extracts `shop`, `topic`, `webhook_id`, and `api_version` directly from HTTP headers, while `to_signable_string` (the value that is actually HMAC-verified) returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes/compares the HMAC exclusively over `verifiable_query.to_signable_string`, i.e. the body: [2](#0-1) 

`Registry.process` checks the HMAC and then immediately constructs `WebhookMetadata` using `request.shop` — the unauthenticated header value — with no cross-check against the shop that actually owns/registered the topic or any session store: [3](#0-2) 

### The broken binding

The equality the library implicitly claims to guarantee is:

```
shop used by handler (WebhookMetadata#shop) == shop that Shopify authenticated via HMAC
```

But because `shop-domain` is a header, not part of `@raw_body`, the HMAC only proves *"this body byte-string was signed with the app's secret"* — it proves nothing about which shop the header claims to be from. Any request whose body matches a previously-observed, validly-signed body (e.g., a generic `{}` payload used by mandatory/compliance topics, or any topic whose body an attacker can predict/replay) will pass `HmacValidator.validate` regardless of the `shop-domain` header value, since that header is never included in `compute_signature`.

This matches the reported bug class ("a field acted on but not covered by the HMAC") applied to the gem's own webhook verification code, rather than the Webpack/LavaMoat context of the source report.

### Why this matters (impact)

Downstream host applications are documented to trust `WebhookMetadata#shop` as the tenant key without additional verification — that is the very field the docs tell developers to use: [4](#0-3) 

An unprivileged actor who can obtain any one validly-signed `(raw_body, hmac)` pair from Shopify (e.g., by triggering a webhook for their own shop, since GDPR/compliance and many event payloads have low-entropy or predictable bodies, or the empty-body case) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. Because the signature check never touches the header, `Registry.process` will accept it and invoke the handler claiming data belongs to a victim shop — leading to cross-tenant data corruption/spoofing in the host application (e.g., a `shop/redact` or `app/uninstalled` webhook falsely attributed to a victim's shop, or state keyed by `data.shop` written under the wrong tenant).

### Recommendation

Include the shop domain (and ideally topic/webhook-id) in the signed/verified material, or require the caller to independently verify `request.shop` corresponds to a shop with which the app has an active installation/session before trusting it, rather than relying solely on the header value passed through `WebhookMetadata`.

### Proof of Concept

1. Install the app on a self-controlled shop, `attacker.myshopify.com`, and capture one legitimately delivered webhook `(raw_body="{}", hmac=H)` for a topic whose body is predictable/constant (e.g. a compliance topic).
2. POST directly to the app's public webhook endpoint:
```
x-shopify-topic: shop/redact
x-shopify-hmac-sha256: <H>   (still valid because it only signs "{}")
x-shopify-shop-domain: victim-shop.myshopify.com
```
3. `HmacValidator.validate` passes because `to_signable_string` only checks the body `"{}"` against `H`.
4. `Registry.process` invokes the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)`, and the host app performs tenant-scoped actions (e.g., data deletion/redaction bookkeeping) against `victim-shop`, despite the HMAC never having authenticated that shop identity. [3](#0-2)

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

**File:** docs/usage/webhooks.md (L123-136)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
```
