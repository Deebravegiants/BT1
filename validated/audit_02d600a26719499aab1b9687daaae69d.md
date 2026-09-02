Confirmed: the `Utils::VerifiableQuery` interface only requires `hmac` and `to_signable_string`, and `Webhooks::Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb:35-38`) returns only `@raw_body`. The `shop`, `topic`, and `webhook_id` values, which are read straight from unauthenticated HTTP headers (`lib/shopify_api/webhooks/request.rb:20-33`), are never included in the HMAC-signed payload, yet `Webhooks::Registry.process` trusts `request.shop` to build `WebhookMetadata` after only checking the body HMAC.

### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the `shop`, `topic`, and `webhook_id` fields that the app's webhook handler actually acts on are taken from headers that are completely outside that signature.

### Finding Description
`Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)` [1](#0-0)  which in turn calls `validate_signature`, comparing the HMAC over `verifiable_query.to_signable_string` [2](#0-1) . For `Webhooks::Request`, `to_signable_string` returns `@raw_body` exclusively [3](#0-2) , while `shop`, `topic`, and `webhook_id` are parsed from the `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` headers with no cryptographic binding to the body or its HMAC [4](#0-3) . After HMAC validation succeeds, `Registry.process` dispatches to the handler using these unauthenticated header values verbatim: `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` [5](#0-4) .

The identity binding that should hold is: `shop authenticated by HMAC == shop the handler acts on`. Because the header carrying `shop` is not part of the signed material, that equality is never enforced. Any party that has ever received one valid webhook body+HMAC pair for one shop (e.g., the operator of their own shop's app installation, who legitimately receives their own webhooks) can resend the identical `raw_body`/`x-shopify-hmac-sha256` pair to the same endpoint while substituting a different `x-shopify-shop-domain` value. The HMAC still validates because it never covered the header, and the handler will process the request believing it originated from the victim shop specified in the forged header — a direct cross-tenant identity-binding break, structurally identical to the private-sale spoofing bug class where the signature covers less than what is subsequently trusted/acted upon.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: an attacker-controlled `shop` value flows into the app's webhook handler as if the events belongs to arbitrary shop domain, even though it never had a valid signature. Any host application that keys its multi-tenant data mutations (order/customer/app-uninstall handling, GDPR data-deletion webhooks, credential/token revocation, etc.) off `WebhookMetadata#shop` without independent verification can be tricked into performing cross-tenant actions or accepting shop-domain-scoped events for a shop the caller never actually owns.

### Likelihood Explanation
Likelihood is limited by the requirement that the attacker already possess one valid `raw_body` + HMAC pair (e.g., from webhooks Shopify sent to their own shop's endpoint) and by the target body needing to be shop-agnostic content (many webhook payloads, like `app/uninstalled` bodies, carry little to no shop-identifying content of their own). It does not require the `api_secret_key`, an access token, or any privileged credential — only observation of one's own legitimate webhook traffic, which is available to any unprivileged merchant/app installer.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the HMAC-signable string in `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind them to the signed body, so `Utils::HmacValidator.validate` cannot succeed unless the shop the handler receives matches the shop Shopify actually signed for.

### Proof of Concept
1. App receives a legitimate webhook for `shop-a.myshopify.com` with body `{}` and header `x-shopify-hmac-sha256: <valid-hmac-of-{}>`.
2. Attacker (owner of `shop-a`) resends the exact same body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: forged_headers)` builds a request whose `hmac` still matches, because `to_signable_string` only ever returns `"{}"` [3](#0-2) .
4. `ShopifyAPI::Webhooks::Registry.process` passes HMAC validation and calls the handler with `shop: "shop-b.myshopify.com"` [6](#0-5) , even though Shopify never issued this webhook for `shop-b`.

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
