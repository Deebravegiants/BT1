I found a concrete identity-binding break: the webhook HMAC signs only the raw body, but the `shop` (and `topic`/`webhook-id`) values used by the receiving app to attribute an event to a tenant come from unauthenticated HTTP headers.### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are trusted for tenant attribution but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values that are handed to the app's webhook handler as the identity of the tenant/event come from HTTP headers that are never included in the signed material, breaking the equality that should hold between "bytes verified" and "bytes acted upon."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes and compares the HMAC exclusively against that signable string (the body), never against the `shop-domain`, `topic`, or `webhook-id` headers: [2](#0-1) 

`Registry.process` accepts the request once the body HMAC checks out, then forwards the *unauthenticated* header-derived `shop`, `topic`, and `webhook_id` straight to the handler: [3](#0-2) 

`Request#shop`, `#topic`, and `#webhook_id` are read directly from headers with no cross-check against the signed body: [4](#0-3) 

The intended security invariant is: `bytes_verified_by_hmac == bytes_the_handler_treats_as_authenticated_for_this_shop`. In this implementation the invariant does not hold: `bytes_verified_by_hmac = raw_body` while `bytes_the_handler_trusts_for_tenant_attribution = raw_body ∪ {shop-domain header, topic header, webhook-id header}`. Because Shopify's own signature scheme (documented HMAC-SHA256 over the body) never covers these headers, any request carrying a body+HMAC pair that is valid for *some* shop can have its headers rewritten to name a *different* shop, topic, or webhook id, and the request still passes `HmacValidator.validate`.

### Impact Explanation
An unauthenticated internet user who controls (or has access to webhooks delivered to) their own installed shop can capture a legitimately-signed webhook (valid body + HMAC, since HMAC uses the app's real `api_secret_key` on Shopify's side) and replay it to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header changed to an arbitrary victim shop domain (and/or the topic/webhook-id changed). `Registry.process` will pass HMAC validation (body unchanged) and dispatch to the handler with `WebhookMetadata#shop` set to the attacker-chosen value. Any host application that uses `shop` from the webhook payload to look up a merchant's session/access token, update per-tenant records, or gate authorization for the delivered `body` will act on data attributed to the wrong tenant — i.e., cross-tenant access/data confusion driven entirely by fields this gem hands the app as if they were authenticated. This satisfies the Critical "cross-tenant access" impact bar, since the compromise originates purely from this gem's `HmacValidator`/`Webhooks::Request` design (body-only signing, header-derived identity) rather than any misuse of documented API by the host app.

### Likelihood Explanation
Likelihood is High: no secret material, privileged account, or credential leak is required. The attacker only needs one legitimately-signed webhook of their own (trivial to obtain by installing/using the target app on their own store) and the ability to send an arbitrary HTTP POST with custom headers to the public webhook endpoint — both are unauthenticated, internet-reachable actions.

### Recommendation
Bind the header-derived identity fields to the signed payload before trusting them: either include `shop-domain`, `topic`, and `webhook-id` in the HMAC signable string (breaking compatibility with Shopify's documented scheme is not possible unilaterally, so instead) validate them against an independently-authenticated source, e.g., require the host application to cross-check `request.shop` against the shop associated with the currently active/looked-up session rather than trusting the header value directly, and document this requirement prominently in `Webhooks::Request`/`Registry`. At minimum, flag in the API that `shop`, `topic`, and `webhook_id` are not covered by the HMAC and must not be used as the sole tenant identifier for security-sensitive operations.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and lets it trigger a webhook (e.g., `orders/create`), capturing the raw POST: body `B` and header `X-Shopify-Hmac-Sha256: H` (valid, since Shopify signs `B` with the app's real secret).
2. Attacker resends the identical body `B` and HMAC header `H` to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and compares against `H` — this matches because `B` is unchanged: [5](#0-4) 
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body_of_B, ...)`, and any tenant-scoped logic in the host app now operates as if this event came from `victim.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
