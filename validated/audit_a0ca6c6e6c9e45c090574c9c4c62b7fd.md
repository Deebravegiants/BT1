I found a strong analog: the webhook request's `shop` (tenant) field is trusted for routing/tenant identification without being covered by the HMAC signature.

### Title
Webhook `shop-domain` / `topic` headers are trusted without being covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the raw HTTP body only, while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated HTTP headers. [1](#0-0) 
`ShopifyAPI::Webhooks::Registry.process` validates the HMAC over that request, but the HMAC only proves the *body* was signed by Shopify's secret — it says nothing about which shop or topic the signature was intended for — and then unconditionally trusts `request.shop`/`request.topic` to dispatch the handler and build `WebhookMetadata`. [2](#0-1) 

### Finding Description
The identity binding that should hold is:
`shop authenticated by HMAC == shop the handler acts on`

In this gem that equality does not hold. `HmacValidator.validate` calls `verifiable_query.to_signable_string`, which for `Webhooks::Request` returns only `@raw_body`: [3](#0-2) 
None of `shop`, `topic`, `webhook_id`, or `api_version` — all read from the `shopify-*`/`x-shopify-*` headers — are included in the signed string: [4](#0-3) 

`HmacValidator.validate_signature` then does a secure comparison of the computed HMAC against `verifiable_query.hmac`, based solely on that body string: [5](#0-4) 

`Registry.process` treats a passing HMAC check as authorization to trust the request's `shop` and `topic` headers, and forwards them straight into the handler's `WebhookMetadata`: [2](#0-1) 

Because the HMAC is body-only, any request that carries a body/HMAC pair Shopify has legitimately signed for shop A's webhook (which the operator of shop A can trivially capture by installing the app and receiving one real webhook, e.g. `app/uninstalled` or `orders/create` with an empty/known body) remains "valid" no matter what `shop-domain`, `topic`, `webhook-id`, or `api-version` headers are substituted. An attacker who controls their own shop (an unprivileged Shopify merchant, no `api_secret_key` needed) can replay that captured body+HMAC with forged headers claiming to be a different `shop-domain`/`topic`, and the gem will accept it as an authentic webhook for the victim tenant.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: the host application's webhook handlers receive `WebhookMetadata` claiming to originate from an arbitrary victim shop, chosen by the attacker, despite the HMAC only ever proving the body came from Shopify for the attacker's own shop. Depending on which webhook topics the host app has registered, this is cross-tenant access — e.g., forging `app/uninstalled` to trigger deletion/deauthorization of a victim shop's stored session, or forging `shop/redact`/`customers/data_request` compliance webhooks to trigger destructive or data-disclosure actions against a shop the attacker does not control. This matches the Critical "cross-tenant access" impact bar.

### Likelihood Explanation
The attacker needs no privileged credential, no `api_secret_key`, and no access token — only the ability to install the app on any shop they control (or observe an empty/known-body webhook payload) and to send an HTTP request to the app's own webhook endpoint with forged headers. The HMAC check as implemented in this gem cannot detect the substitution because it never covers the headers, so this is directly exploitable through the gem's documented API surface (`ShopifyAPI::Webhooks::Request.new` + `ShopifyAPI::Webhooks::Registry.process`).

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` (or at minimum `shop` and `topic`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the body before trusting them for dispatch — e.g., verify that the `shop-domain` header matches an expected/registered shop for the currently authenticated session/tenant context, rather than trusting it merely because the body-only HMAC passed.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and captures one legitimately delivered webhook, e.g. body `"{}"` with header `x-shopify-hmac-sha256: <valid-hmac-of-"{}">` and `x-shopify-topic: orders/create`.
2. Attacker resends this exact body and HMAC header to the app's webhook endpoint, but with headers changed to `x-shopify-shop-domain: victim-shop.myshopify.com` and `x-shopify-topic: app/uninstalled`.
3. `ShopifyAPI::Webhooks::Request.new` parses these forged headers; `Registry.process` calls `HmacValidator.validate(request)`, which recomputes the HMAC over `"{}"` only and it matches, since the header values were never part of the signed payload. [6](#0-5) 
4. The registered `app/uninstalled` handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the host app to act (e.g., delete/deauthorize the victim's session) as though Shopify itself had signed a webhook for `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
