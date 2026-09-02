### Title
Webhook shop-domain identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the unauthenticated `x-shopify-shop-domain` header, while `Utils::HmacValidator` only verifies the raw request body. The header carrying the tenant identity is never part of the signed material, so it can be swapped without invalidating the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `HmacValidator.validate`/`validate_signature` compute the HMAC strictly over `verifiable_query.to_signable_string`, i.e. only the body bytes: [2](#0-1) .

However, `Request#shop` is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header, a value that is not part of the signed content: [3](#0-2) .

`Registry.process` validates the HMAC of the body and, once that succeeds, trusts `request.shop` and forwards it to the handler as the tenant identifier without any additional check that this header corresponds to the shop that actually produced the signed body: [4](#0-3) .

This breaks the intended identity binding: `shop-domain header == shop that produced the signed body` is never enforced; only `hmac(body) == valid` is enforced. Since every shop installed on a given app shares the same `client_secret`/`api_secret_key` used to compute the webhook HMAC, a valid `(body, hmac)` pair generated for shop A's real webhook event remains a valid `(body, hmac)` pair regardless of which shop-domain header accompanies it.

### Impact Explanation
An unprivileged internet user who controls a shop that has the target app installed (trivial to obtain via a free/dev store) can:
1. Trigger a real webhook event on their own shop, capturing the legitimately Shopify-signed `raw_body` and `x-shopify-hmac-sha256` value delivered to the app's webhook endpoint.
2. Replay that exact `(raw_body, hmac)` pair to the same multi-tenant webhook endpoint, but substitute the `x-shopify-shop-domain` header with a victim shop's domain.
3. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` invokes the handler with `WebhookMetadata` whose `shop` field is now the victim's domain: [5](#0-4) .

If the host application uses `WebhookMetadata#shop` as the tenant key to look up the session/access token, update tenant-scoped records, or route further API calls, this results in cross-tenant data injection/corruption — data attributed to or acted on behalf of a shop that never sent it. This satisfies the "Critical – cross-tenant access" impact bar, since the shop identity binding that gates all subsequent tenant-scoped processing is defeated using only a forged header, no credentials of the victim shop required.

### Likelihood Explanation
Likelihood is high for any app that (a) shares one webhook endpoint across all installed shops (the standard, documented pattern for this gem) and (b) trusts `WebhookMetadata#shop` to select the tenant context, which is the expected usage shown in the gem's own webhook handler examples. The only prerequisite is that the attacker installs the app on a shop they control (self-service, no privilege) and can capture one webhook delivery to obtain a valid `(body, hmac)` pair — something they can always do by triggering an event on their own store.

### Recommendation
Bind the header-derived shop identity to the signed content: either include `shop_domain` (and ideally `topic`/`webhook_id`) inside `to_signable_string` so tampering invalidates the HMAC, or have `Registry.process`/consuming apps cross-check `request.shop` against the shop associated with the session/install record that is expected to be receiving that specific webhook topic before trusting it as the tenant key.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" with the app installed.
# 1. Trigger any webhook event on their own shop; capture the delivered
#    raw body and the "x-shopify-hmac-sha256" header Shopify computed for it.
captured_body = raw_body_from_real_delivery
captured_hmac = headers_from_real_delivery["x-shopify-hmac-sha256"]

# 2. Replay against the app's shared webhook endpoint, swapping only the
#    shop-domain header to the victim's shop.
forged_headers = {
  "x-shopify-topic"        => headers_from_real_delivery["x-shopify-topic"],
  "x-shopify-hmac-sha256"  => captured_hmac,          # unchanged, still valid
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # forged
  "x-shopify-webhook-id"   => headers_from_real_delivery["x-shopify-webhook-id"],
  "x-shopify-api-version"  => headers_from_real_delivery["x-shopify-api-version"],
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: forged_headers)

# HmacValidator.validate(request) => true, because it only checks captured_body/captured_hmac
ShopifyAPI::Webhooks::Registry.process(request)
# handler.handle receives WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
# even though the signed payload never originated from victim-shop.
```

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
