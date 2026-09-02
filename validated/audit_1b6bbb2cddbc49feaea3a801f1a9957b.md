## Title
Webhook `shop` identity field is not covered by the HMAC signature, allowing tenant-spoofing in `Registry.process` - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC over the raw request body only, then dispatches the handler using a `shop` value that is taken from an HTTP header that is completely outside the HMAC's signed content. An unprivileged internet user who can replay or forge a POST with a body/HMAC pair (e.g. a body they legitimately received for their own shop, or any body whose HMAC they can compute if they ever obtain any valid `(body, hmac)` pair) can supply an arbitrary `x-shopify-shop-domain` header, and the handler will process the webhook as if it belongs to that spoofed shop.

### Finding Description
`Utils::VerifiableQuery`/`HmacValidator.validate` calls `to_signable_string`, and for webhook requests this is defined as just the raw body: [1](#0-0) 

The `shop` accessor, however, is read straight from the `shop-domain` header, which is never part of the signed bytes: [2](#0-1) 

`Registry.process` validates the HMAC of the request and, on success, immediately trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` passed to the app's handler, without any additional binding between the shop header and the signed payload: [3](#0-2) 

This breaks the intended identity binding: `HMAC-verified bytes == bytes acted upon`. In Shopify's real webhook contract, `hmac == HMAC(secret, raw_body)` proves the body is genuine, but it says nothing about which shop the header claims sent it. The gem's `HmacValidator.validate` (shared with OAuth) only proves that *some* valid webhook was sent by Shopify for *some* shop; it does not prove the shop identifier the app receives is the one that produced that HMAC. [4](#0-3) 

### Impact Explanation
Any host application (including reference integrations like the `shopify_app` gem) that follows this library's documented contract — "the HMAC is valid, therefore this is an authentic webhook for `request.shop`" — inherits a tenant-confusion vulnerability. Because `shop` is not part of the signed content, an attacker who is able to obtain any single valid `(raw_body, hmac)` pair from Shopify (e.g. because they run their own shop/app installation and receive real webhooks for it) can resend that exact byte-for-byte payload with a different `shop-domain` header. `Utils::HmacValidator.validate` will still succeed (it only checks the body), and `Registry.process` will hand the handler a `WebhookMetadata` claiming a different, victim shop. If the host application uses `request.shop`/`WebhookMetadata#shop` to look up per-tenant data, credentials, or to key mutations (a common pattern), this allows cross-tenant data confusion/injection using another merchant's identity — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is bounded by the requirement that the attacker already possess a valid `(body, hmac)` pair for *some* shop (their own installed app instance is sufficient — no privileged credential of the target is needed). Given that constraint is easy to satisfy for any developer/attacker who can install their own shop or trigger webhooks for their own tenant, and that the vulnerable code path (`Registry.process` → `HmacValidator.validate` → trust `request.shop`) is the library's primary/documented API surface for webhook handling, exploitation requires no `api_secret_key`, no access token, and no social engineering — only the ability to send an HTTP POST with attacker-chosen headers.

### Recommendation
Include the `shop-domain` (and `topic`) header values in the signed material that `HmacValidator` verifies for webhook requests, or otherwise cryptographically bind `request.shop` to the HMAC-covered body (e.g., verify shop/topic against a value embedded in the payload, or require the host application to cross-check `shop` against a known/registered value before trusting it). At minimum, document prominently that `request.shop` is unauthenticated and must not be trusted for tenant-scoping decisions without independent verification.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and receives a legitimate webhook: raw body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B`), `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the exact same `B`/`H` pair to the app's webhook endpoint but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H})` is constructed.
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation passes: [5](#0-4) 
5. The registered handler is invoked with `WebhookMetadata` where `shop: "victim.myshopify.com"`, even though the body actually originated from/for `attacker.myshopify.com`: [6](#0-5) 

**Uncertainty note:** I could not fully explore the host-application-facing `WebhookMetadata`/`WebhookHandler` interface or any downstream `shopify_app` reference-integration code within index limits, so I cannot confirm how commonly `shop` is used for authorization decisions versus merely logging in real deployments; the severity assessment assumes the documented, expected usage pattern (keying data operations off `WebhookMetadata#shop`).

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
