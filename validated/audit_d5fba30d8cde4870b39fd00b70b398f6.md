Confirmed: the `VerifiableQuery` interface requires only `hmac` and `to_signable_string`, and `Webhooks::Request#to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `api_version`, and `webhook_id` come from unauthenticated HTTP headers. This is a genuine identity-binding gap in the gem's own webhook-processing code.

### Title
Webhook shop/topic attribution is not covered by HMAC, allowing cross-tenant webhook spoofing via header substitution - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` trusts the `shop`, `topic`, `api_version`, and `webhook_id` values taken from HTTP headers when dispatching webhook data to the host application's handler, but the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body, not these headers.

### Finding Description
`Webhooks::Request` implements the `Utils::VerifiableQuery` interface, whose contract only binds `hmac` to `to_signable_string`: [1](#0-0) 

`Webhooks::Request#to_signable_string` returns solely `@raw_body`: [2](#0-1) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from HTTP headers, which are not part of the signed material: [3](#0-2) 

`Registry.process` validates only the HMAC over the body, then forwards the header-derived `shop` value straight into `WebhookMetadata` passed to the host app's handler, with no cross-check binding `shop` to the signed body: [4](#0-3) 

This breaks the identity binding `shop_verified_by_signature == shop_used_by_handler`: the equality that should hold is that the tenant identifier acted upon (`data.shop`) is the same tenant identifier whose secret produced the HMAC over the payload. Because only the body is signed, an entity capable of capturing one legitimately HMAC'd webhook delivery (e.g., a merchant/store operator receiving webhooks for their own shop, who is an unprivileged actor with respect to any *other* tenant using the same app) can replay the same `raw_body` + `hmac-sha256` value while substituting the `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`) headers. The HMAC check still passes because it only verifies the body bytes, yet the handler receives an attacker-chosen `shop` value.

### Impact Explanation
This is a cross-tenant identity-binding failure: a webhook payload cryptographically tied only to "some data signed with the app's secret" gets attributed to an arbitrary `shop` value chosen by the request sender. If a host application uses `WebhookMetadata#shop` to select which merchant's session/data to update, delete, or act upon (the documented and intended use per `docs/usage/webhooks.md`), an attacker can cause the app to process webhook data under a victim tenant's identity, i.e., cross-tenant access/action confusion, without ever possessing the app's `client_secret` or any victim credential.

### Likelihood Explanation
Exploitation requires only network-level ability to send an HTTP POST to the app's webhook endpoint with a previously-observed valid `(raw_body, hmac-sha256)` pair and forged `shop`, `topic`, `webhook_id` headers — none of which require the `api_secret_key` or any privileged credential, since those fields sit entirely outside the HMAC-signed data. The gem provides no header-binding, timestamp/nonce, or replay protection beyond the raw-body HMAC.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the signable string computed by `Webhooks::Request#to_signable_string` (or otherwise cryptographically bind them to the HMAC verification), so that `Registry.process` cannot dispatch handler data whose `shop`/`topic` attribution was never covered by the signature. At minimum, document and/or enforce that host applications must not trust `data.shop`/`data.topic` without an independent, signature-bound check.

### Proof of Concept
1. App receives a legitimate webhook for `attacker-shop.myshopify.com` with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC_SHA256(secret, B)`.
2. Attacker (who controls delivery to their own webhook endpoint or a proxy in front of it) resends the same `B` and `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and, if desired, a different `x-shopify-topic`/`x-shopify-webhook-id`.
3. `Utils::HmacValidator.validate` succeeds because it only recomputes the HMAC over `B` via `to_signable_string`: [5](#0-4) 
4. `Registry.process` raises no error and calls the host's handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` where `shop` is `"victim-shop.myshopify.com"`, even though the signed body never originated from or referenced that shop: [6](#0-5)

### Citations

**File:** lib/shopify_api/utils/verifiable_query.rb (L11-16)
```ruby
      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
```

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
