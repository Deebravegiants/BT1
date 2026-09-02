Based on my analysis, here is the analog vulnerability found in this gem.

### Title
Webhook `shop` domain is trusted for tenant routing without HMAC coverage, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
The bug report describes a system where a security check (address signature) is disconnected from the actual authorization boundary (any address can be subscribed via the backend regardless of signature), so the "proof" provides no real guarantee. The closest structural analog in this gem is `ShopifyAPI::Webhooks::Request`: the HMAC signature that Shopify computes and this gem validates covers only the raw request body, while the `shop` value used to identify *which tenant* the webhook belongs to is read from an HTTP header that is completely outside the HMAC's coverage. The library treats "HMAC valid" as equivalent to "this event, including its claimed shop, is authentic," which is the same kind of broken identity binding as the reported issue.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never included in the HMAC computation: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`, `request.api_version` — also unsigned headers) to build the `WebhookMetadata` that is handed to the host application's handler: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` confirm this: they only ever operate on `verifiable_query.to_signable_string`, i.e., the body, via `OpenSSL.secure_compare`: [4](#0-3) 

The equality the library implicitly assumes is:

`shop used to identify the tenant for webhook processing == shop that produced the HMAC-signed payload`

But because the HMAC only binds the body bytes, this equality does not hold. An entity that legitimately receives one valid `(body, hmac)` pair for *any* shop under the same app (e.g., their own store where they installed the app) can replay that exact body with a *different* `x-shopify-shop-domain` header value. `HmacValidator.validate` still succeeds because it never inspects headers, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the body belongs to the attacker-chosen `shop`.

### Impact Explanation
Any application built on this gem that uses `WebhookMetadata#shop` to route webhook data per-tenant (the standard pattern documented for this gem, and the only field the gem exposes for that purpose) can be made to store or act on data under the wrong shop/tenant. This is a cross-tenant confusion primitive at the library layer: this gem hands the host app an unauthenticated tenant identifier alongside "HMAC verified" status, creating the false impression that the whole event, including shop attribution, is authentic.

### Likelihood Explanation
Exploitation only requires the ability to receive one legitimate webhook delivery from Shopify for any shop that has the target app installed (e.g., an attacker's own store), plus the ability to POST an HTTP request with attacker-controlled headers to the app's webhook endpoint. No access to `api_secret_key`, access tokens, or any credential is required — only observation of one real webhook delivery.

### Recommendation
`ShopifyAPI::Webhooks::Request#to_signable_string` should not be the sole authenticity anchor for `shop`; the library should either document/enforce that the `shop` header must be cross-checked against a shop known to have a valid session/installation before being trusted for routing, or better, the gem should refuse to expose `shop`/`topic`/`webhook_id` as trusted fields unless there is an accompanying mechanism (e.g., requiring the caller to pass the expected shop and comparing it) that binds the header to the HMAC-covered body.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and legitimately receives a webhook `POST` with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker replays this exact request to the app's webhook endpoint, keeping body `B` and the HMAC header unchanged, but rewrites `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC.
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)`, and any host logic keyed on `data.shop` (session lookup, per-tenant storage, redaction/GDPR flows, etc.) processes attacker-supplied data as if it came from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
